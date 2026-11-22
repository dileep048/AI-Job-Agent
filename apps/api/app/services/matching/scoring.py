from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any

from app.models.experience import Experience
from app.models.profile import CandidateProfile
from app.models.skill import CandidateSkill
from app.services.matching.requirements import JobRequirements
from app.services.matching.semantic import cosine_similarity
from app.services.matching.skills import skills_match

WEIGHTS = {
    "skills": 0.35,
    "experience": 0.20,
    "location": 0.15,
    "salary": 0.10,
    "semantic": 0.20,
}


@dataclass
class DimensionScores:
    skill: float
    experience: float
    location: float
    salary: float
    semantic: float
    overall: float
    recommendation: str
    matched_skills: list[str]
    missing_skills: list[str]
    breakdown: dict[str, Any]


def score_match(
    *,
    profile: CandidateProfile,
    skills: list[CandidateSkill],
    experiences: list[Experience],
    requirements: JobRequirements,
    job_title: str,
    job_description: str | None,
) -> DimensionScores:
    matched, missing, skill_score = _skill_scores(skills, experiences, requirements.skills)
    experience_score = _experience_score(profile, experiences, requirements.years_required)
    location_score = _location_score(profile, requirements)
    salary_score = _salary_score(profile, requirements)
    semantic_score = _semantic_score(profile, experiences, skills, job_title, job_description)
    overall = round(
        skill_score * WEIGHTS["skills"]
        + experience_score * WEIGHTS["experience"]
        + location_score * WEIGHTS["location"]
        + salary_score * WEIGHTS["salary"]
        + semantic_score * WEIGHTS["semantic"],
        1,
    )
    return DimensionScores(
        skill=skill_score,
        experience=experience_score,
        location=location_score,
        salary=salary_score,
        semantic=semantic_score,
        overall=overall,
        recommendation=_recommendation(overall),
        matched_skills=matched,
        missing_skills=missing,
        breakdown={
            "weights": WEIGHTS,
            "candidate_years": _candidate_years(profile, experiences),
            "years_required": requirements.years_required,
            "job_type_aligned": _job_type_aligned(profile, requirements.employment_type),
        },
    )


def _skill_scores(
    skills: list[CandidateSkill],
    experiences: list[Experience],
    required: list[str],
) -> tuple[list[str], list[str], float]:
    candidate = [item.skill_name for item in skills]
    for experience in experiences:
        candidate.extend(str(tech) for tech in (experience.technologies or []))
    if not required:
        return [], [], 50.0
    matched: list[str] = []
    missing: list[str] = []
    for skill in required:
        if any(skills_match(skill, item) for item in candidate):
            matched.append(skill)
        else:
            missing.append(skill)
    return matched, missing, round(100.0 * len(matched) / len(required), 1)


def _candidate_years(profile: CandidateProfile, experiences: list[Experience]) -> int | None:
    if profile.years_experience is not None:
        return int(profile.years_experience)
    if not experiences:
        return None
    today = date.today()
    months = 0
    for item in experiences:
        end = item.end_date or today
        start = item.start_date
        months += max((end.year - start.year) * 12 + (end.month - start.month), 0)
    return months // 12


def _experience_score(
    profile: CandidateProfile, experiences: list[Experience], required: int | None
) -> float:
    years = _candidate_years(profile, experiences)
    if required is None or years is None:
        return 50.0
    if years >= required:
        return 100.0
    if years >= max(required - 1, 0):
        return 75.0
    return round(max(0.0, 100.0 * years / required), 1)


def _location_score(profile: CandidateProfile, requirements: JobRequirements) -> float:
    workplace = (requirements.workplace_type or "").lower()
    preference = (profile.remote_preference or "").lower()
    job_locations = " ".join(requirements.locations).lower()
    remote_job = workplace == "remote" or "remote" in job_locations
    preferred = [item.lower() for item in (profile.preferred_locations or []) if item]

    if remote_job and preference in {"remote", "hybrid", "flexible", "any"}:
        return 100.0
    if remote_job and preference == "onsite":
        return 40.0
    if workplace == "onsite" and preference == "remote":
        return 25.0
    if not preferred and not preference:
        return 50.0
    if preferred and any(
        loc in job_locations or job_locations in loc for loc in preferred if loc
    ):
        return 100.0
    if preferred and job_locations:
        return 35.0
    if workplace == "hybrid" and preference in {"hybrid", "remote", "flexible"}:
        return 80.0
    return 50.0


def _salary_score(profile: CandidateProfile, requirements: JobRequirements) -> float:
    cand_min = _num(profile.minimum_salary)
    cand_max = _num(profile.maximum_salary)
    job_min = requirements.salary_min
    job_max = requirements.salary_max
    if job_min is None and job_max is None:
        return 50.0
    if cand_min is None and cand_max is None:
        return 50.0
    cand_currency = (profile.salary_currency or "").upper()
    job_currency = (requirements.salary_currency or "").upper()
    if cand_currency and job_currency and cand_currency != job_currency:
        return 50.0
    job_high = job_max if job_max is not None else job_min
    job_low = job_min if job_min is not None else job_max
    if cand_min is not None and job_high is not None and job_high < cand_min:
        return 20.0
    if cand_max is not None and job_low is not None and job_low > cand_max:
        return 70.0
    return 100.0


def _semantic_score(
    profile: CandidateProfile,
    experiences: list[Experience],
    skills: list[CandidateSkill],
    title: str,
    description: str | None,
) -> float:
    profile_text = " ".join(
        [
            profile.headline or "",
            profile.summary or "",
            profile.current_role or "",
            *[skill.skill_name for skill in skills],
            *[
                f"{item.job_title} {item.description or ''} {' '.join(str(t) for t in item.technologies or [])}"
                for item in experiences
            ],
        ]
    )
    job_text = f"{title} {description or ''}"
    similarity = cosine_similarity(profile_text, job_text)
    return round(similarity * 100.0, 1)


def _job_type_aligned(profile: CandidateProfile, employment_type: str | None) -> bool | None:
    preferred = [item.lower().replace("-", "_").replace(" ", "_") for item in (profile.preferred_job_types or [])]
    if not preferred or not employment_type:
        return None
    job_type = employment_type.lower().replace("-", "_").replace(" ", "_")
    return any(job_type in item or item in job_type for item in preferred)


def _recommendation(score: float) -> str:
    if score >= 75:
        return "APPLY"
    if score >= 50:
        return "CONSIDER"
    return "SKIP"


def _num(value: Decimal | float | int | None) -> float | None:
    if value is None:
        return None
    return float(value)
