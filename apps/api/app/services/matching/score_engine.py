from __future__ import annotations

from app.services.matching.config import get_match_weights
from app.services.matching.dto import CandidateEvidence, HardFilterResult, JobRequirements, MatchResult
from app.services.matching.experience_matcher import match_experience
from app.services.matching.hard_filter import apply_hard_filters
from app.services.matching.location_matcher import match_employment, match_location, match_workplace
from app.services.matching.salary_matcher import match_salary
from app.services.matching.semantic_matcher import match_semantic
from app.services.matching.skill_matcher import match_skills
from app.services.matching.title_matcher import match_title


def compute_match(
    candidate: CandidateEvidence,
    requirements: JobRequirements,
    *,
    job_description: str | None,
    hard_filter: HardFilterResult | None = None,
) -> MatchResult:
    weights = get_match_weights()
    hard = hard_filter or apply_hard_filters(candidate, requirements)
    matched, missing, preferred_matched, skill_score = match_skills(
        candidate,
        requirements.required_skills,
        requirements.preferred_skills,
    )
    experience_score, candidate_years, required_years = match_experience(candidate, requirements)
    title_score = match_title(candidate, requirements)
    location_score = match_location(candidate, requirements)
    workplace_score = match_workplace(candidate, requirements)
    employment_score = match_employment(candidate, requirements)
    salary_score, salary_match = match_salary(candidate, requirements)
    semantic_score = match_semantic(candidate, requirements, job_description)

    structured = weights.structured_weights()
    overall = (
        skill_score * structured["skills"]
        + experience_score * structured["experience"]
        + title_score * structured["title"]
        + location_score * structured["location"]
        + workplace_score * structured["workplace"]
        + employment_score * structured["employment"]
        + salary_score * structured["salary"]
        + semantic_score * weights.semantic_weight()
    )
    overall = round(min(max(overall, 0.0), 100.0), 1)
    recommendation = _recommendation(overall, weights.match_apply_threshold, weights.match_consider_threshold)
    if not hard.passed:
        recommendation = "SKIP"
        overall = min(overall, weights.match_consider_threshold - 1)

    strengths, concerns = _insights(
        matched,
        missing,
        candidate_years,
        required_years,
        salary_match,
        hard,
        preferred_matched,
    )
    return MatchResult(
        score=overall,
        recommendation=recommendation,
        confidence=round(overall / 100.0, 2),
        matched_skills=matched,
        missing_skills=missing,
        preferred_matched=preferred_matched,
        skill_score=skill_score,
        experience_score=experience_score,
        title_score=title_score,
        location_score=location_score,
        workplace_score=workplace_score,
        employment_score=employment_score,
        salary_score=salary_score,
        semantic_score=semantic_score,
        strengths=strengths,
        concerns=concerns,
        hard_filter=hard,
        breakdown={
            "weights": {**structured, "semantic": weights.semantic_weight()},
            "experience_match": {
                "score": round(experience_score / 100.0, 2),
                "candidate_years": candidate_years,
                "required_years": required_years,
            },
            "location_match": location_score >= 70,
            "salary_match": salary_match,
            "title_score": title_score,
            "workplace_score": workplace_score,
            "employment_score": employment_score,
        },
    )


def _recommendation(score: float, apply_threshold: float, consider_threshold: float) -> str:
    if score >= apply_threshold:
        return "APPLY"
    if score >= consider_threshold:
        return "CONSIDER"
    return "SKIP"


def _insights(
    matched: list[str],
    missing: list[str],
    candidate_years: int | None,
    required_years: int | None,
    salary_match: bool | None,
    hard: HardFilterResult,
    preferred_matched: list[str],
) -> tuple[list[str], list[str]]:
    strengths: list[str] = []
    concerns: list[str] = list(hard.reasons)
    if matched:
        strengths.append(f"Matches {len(matched)} required skills including {', '.join(matched[:4])}")
    if preferred_matched:
        strengths.append(f"Also aligns with preferred skills: {', '.join(preferred_matched[:4])}")
    if candidate_years is not None and required_years is not None and candidate_years >= required_years:
        strengths.append(f"Meets experience requirement ({candidate_years} vs {required_years}+ years)")
    elif required_years is not None and candidate_years is not None and candidate_years < required_years:
        concerns.append(f"Listed experience ({candidate_years} years) is below stated requirement ({required_years}+)")
    for skill in missing[:6]:
        concerns.append(f"{skill} is not listed in candidate profile")
    if salary_match is False:
        concerns.append("Salary range appears below candidate minimum")
    return strengths[:8], concerns[:10]
