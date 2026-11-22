from __future__ import annotations

import hashlib
import logging
from math import ceil
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.config import get_settings
from app.exceptions import NotFoundError, ValidationAppError
from app.models.job import Job
from app.models.job_match import JobMatch
from app.repositories.education_repository import EducationRepository
from app.repositories.experience_repository import ExperienceRepository
from app.repositories.job_match_repository import JobMatchRepository
from app.repositories.job_repository import JobRepository, JobSearchFilters
from app.repositories.profile_repository import ProfileRepository
from app.repositories.skill_repository import SkillRepository
from app.schemas.job import JobListItem
from app.schemas.match import JobMatchListResponse, JobMatchResponse, MatchScoreSummary
from app.services.matching.candidate_evidence import build_candidate_evidence
from app.services.matching.config import ALGORITHM_VERSION
from app.services.matching.explanation import build_explanation
from app.services.matching.llm import explain_with_llm
from app.services.matching.requirement_extractor import extract_job_requirements
from app.services.matching.score_engine import compute_match

logger = logging.getLogger("ai_job_agent")


class MatchService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.jobs = JobRepository(db)
        self.matches = JobMatchRepository(db)
        self.profiles = ProfileRepository(db)
        self.skills = SkillRepository(db)
        self.experiences = ExperienceRepository(db)
        self.educations = EducationRepository(db)
        self.settings = get_settings()

    def get(self, user_id: UUID, job_id: UUID) -> JobMatchResponse:
        match = self._owned_match(user_id, job_id)
        if match is None:
            raise NotFoundError("MATCH_NOT_FOUND", "No match score for this job yet")
        return self._to_response(match)

    def get_by_id(self, user_id: UUID, match_id: UUID) -> JobMatchResponse:
        match = self.matches.get_by_id_for_user(match_id, user_id)
        if match is None:
            raise NotFoundError("MATCH_NOT_FOUND", "Match not found")
        return self._to_response(match)

    def score_job(self, user_id: UUID, job_id: UUID, *, use_llm: bool = True) -> JobMatchResponse:
        job = self.jobs.get_by_id(job_id)
        if job is None:
            raise NotFoundError("JOB_NOT_FOUND", "Job not found")
        profile, skills, experiences, educations = self._load_candidate(user_id)
        candidate = build_candidate_evidence(profile, skills, experiences, educations)
        digest = _inputs_hash(profile, job, skills, experiences, educations)
        existing = self.matches.get_for_profile_job(profile.id, job_id)
        if existing and existing.inputs_hash == digest and existing.algorithm_version == ALGORITHM_VERSION:
            logger.info("match cache hit job_id=%s profile_id=%s", job_id, profile.id)
            return self._to_response(existing)

        logger.info(
            "match started job_id=%s profile_id=%s algorithm_version=%s",
            job_id,
            profile.id,
            ALGORITHM_VERSION,
        )
        requirements = extract_job_requirements(
            title=job.title,
            description=job.description,
            structured_skills=[item.skill_name for item in job.skills],
            location=job.location,
            locations=list(job.locations or []),
            workplace_type=job.workplace_type,
            employment_type=job.employment_type,
            experience_level=job.experience_level,
            salary_min=_float(job.salary_min),
            salary_max=_float(job.salary_max),
            salary_currency=job.salary_currency,
            use_llm=use_llm,
        )
        result = compute_match(candidate, requirements, job_description=job.description)
        explanation = build_explanation(result, requirements)
        source = "rules"
        ai_reasoning: dict[str, Any] = {}
        model_name = None
        model_version = None
        if use_llm:
            reasoning = explain_with_llm(result, requirements)
            if reasoning:
                explanation = reasoning.summary
                result.strengths = reasoning.strengths or result.strengths
                result.concerns = reasoning.concerns or result.concerns
                ai_reasoning = reasoning.model_dump()
                source = "llm"
                model_name = self.settings.openai_model
                model_version = "chat-completions-json"

        match = existing or JobMatch(user_id=user_id, profile_id=profile.id, job_id=job_id)
        self._apply_result(match, result, requirements, candidate, explanation, source, digest, ai_reasoning, model_name, model_version)
        saved = self.matches.save(match)
        saved.job = job
        logger.info("match completed job_id=%s profile_id=%s score=%s", job_id, profile.id, result.score)
        return self._to_response(saved)

    def list_matches(
        self,
        user_id: UUID,
        *,
        page: int,
        page_size: int,
        min_score: float | None = None,
        recommendation: str | None = None,
        company: str | None = None,
        location: str | None = None,
        workplace_type: str | None = None,
    ) -> JobMatchListResponse:
        profile = self.profiles.get_by_user_id(user_id)
        if profile is None:
            return JobMatchListResponse(items=[], page=page, page_size=page_size, total=0, total_pages=0)
        items, total = self.matches.list_for_profile(
            profile.id,
            page=page,
            page_size=page_size,
            min_score=min_score,
            recommendation=recommendation,
            company=company,
            location=location,
            workplace_type=workplace_type,
        )
        total_pages = ceil(total / page_size) if total else 0
        return JobMatchListResponse(
            items=[self._to_response(item) for item in items],
            page=max(page, 1),
            page_size=min(max(page_size, 1), 100),
            total=total,
            total_pages=total_pages,
        )

    def score_jobs(self, user_id: UUID, job_ids: list[UUID], *, use_llm: bool = False) -> list[JobMatchResponse]:
        unique = list(dict.fromkeys(job_ids))[:20]
        return [self.score_job(user_id, job_id, use_llm=use_llm) for job_id in unique]

    def score_latest(self, user_id: UUID, *, limit: int = 50) -> list[JobMatchResponse]:
        jobs, _total = self.jobs.search(
            JobSearchFilters(is_active=True), page=1, page_size=min(max(limit, 1), 100)
        )
        return [self.score_job(user_id, job.id, use_llm=False) for job in jobs]

    def summaries_for_jobs(self, user_id: UUID, job_ids: list[UUID]) -> dict[UUID, MatchScoreSummary]:
        profile = self.profiles.get_by_user_id(user_id)
        if profile is None or not job_ids:
            return {}
        matches = self.matches.scores_for_profile_jobs(profile.id, job_ids)
        return {
            job_id: MatchScoreSummary(
                overall_score=float(match.overall_score),
                recommendation=match.recommendation,
            )
            for job_id, match in matches.items()
        }

    def stats(self, user_id: UUID) -> dict[str, Any]:
        profile = self.profiles.get_by_user_id(user_id)
        if profile is None:
            return {
                "total_matches": 0,
                "strong_matches": 0,
                "potential_matches": 0,
                "average_score": None,
            }
        return self.matches.stats_for_profile(profile.id)

    def _owned_match(self, user_id: UUID, job_id: UUID) -> JobMatch | None:
        profile = self.profiles.get_by_user_id(user_id)
        if profile is None:
            return None
        return self.matches.get_for_profile_job(profile.id, job_id)

    def _load_candidate(self, user_id: UUID):
        profile = self.profiles.get_by_user_id(user_id)
        if profile is None:
            raise ValidationAppError(
                "PROFILE_REQUIRED",
                "Create a candidate profile before scoring jobs",
            )
        skills = self.skills.list_by_profile(profile.id)
        experiences = self.experiences.list_by_profile(profile.id)
        educations = self.educations.list_by_profile(profile.id)
        return profile, skills, experiences, educations

    def _apply_result(
        self,
        match: JobMatch,
        result,
        requirements,
        candidate,
        explanation: str,
        source: str,
        digest: str,
        ai_reasoning: dict[str, Any],
        model_name: str | None,
        model_version: str | None,
    ) -> None:
        match.overall_score = result.score
        match.skill_score = result.skill_score
        match.experience_score = result.experience_score
        match.title_score = result.title_score
        match.location_score = result.location_score
        match.workplace_score = result.workplace_score
        match.employment_score = result.employment_score
        match.salary_score = result.salary_score
        match.semantic_score = result.semantic_score
        match.recommendation = result.recommendation
        match.confidence = result.confidence
        match.matched_skills = result.matched_skills
        match.missing_skills = result.missing_skills
        match.strengths = result.strengths
        match.concerns = result.concerns
        match.requirements = requirements.as_dict()
        match.candidate_evidence = candidate.as_dict()
        match.structured_score = result.breakdown
        match.breakdown = result.breakdown
        match.ai_reasoning = ai_reasoning
        match.explanation = explanation
        match.explanation_source = source
        match.hard_filter_passed = result.hard_filter.passed
        match.hard_filter_reasons = result.hard_filter.reasons
        match.inputs_hash = digest
        match.algorithm_version = ALGORITHM_VERSION
        match.model_name = model_name
        match.model_version = model_version

    def _to_response(self, match: JobMatch) -> JobMatchResponse:
        job_item = JobListItem.model_validate(match.job) if match.job is not None else None
        return JobMatchResponse(
            id=match.id,
            job_id=match.job_id,
            profile_id=match.profile_id,
            score=float(match.overall_score),
            overall_score=float(match.overall_score),
            skill_score=float(match.skill_score),
            experience_score=float(match.experience_score),
            title_score=float(match.title_score),
            location_score=float(match.location_score),
            workplace_score=float(match.workplace_score),
            employment_score=float(match.employment_score),
            salary_score=float(match.salary_score),
            semantic_score=float(match.semantic_score),
            recommendation=match.recommendation,
            confidence=float(match.confidence),
            matched_skills=list(match.matched_skills or []),
            missing_skills=list(match.missing_skills or []),
            strengths=list(match.strengths or []),
            concerns=list(match.concerns or []),
            requirements=dict(match.requirements or {}),
            breakdown=dict(match.breakdown or {}),
            structured_score=dict(match.structured_score or {}),
            hard_filter_passed=match.hard_filter_passed,
            hard_filter_reasons=list(match.hard_filter_reasons or []),
            explanation=match.explanation,
            explanation_source=match.explanation_source,
            algorithm_version=match.algorithm_version,
            created_at=match.created_at,
            updated_at=match.updated_at,
            job=job_item,
        )


def _float(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def _inputs_hash(profile, job: Job, skills, experiences, educations) -> str:
    skill_part = ",".join(sorted(item.skill_name.lower() for item in skills))
    exp_part = ",".join(sorted(f"{item.id}:{item.updated_at.isoformat()}" for item in experiences))
    edu_part = ",".join(sorted(f"{item.id}:{item.updated_at.isoformat()}" for item in educations))
    raw = "|".join(
        [
            str(profile.id),
            str(job.id),
            job.content_hash,
            str(job.updated_at.isoformat()),
            str(profile.updated_at.isoformat()),
            skill_part,
            exp_part,
            edu_part,
            ALGORITHM_VERSION,
        ]
    )
    return hashlib.sha256(raw.encode()).hexdigest()
