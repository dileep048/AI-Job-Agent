from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.models.education import Education
from app.models.experience import Experience
from app.models.profile import CandidateProfile
from app.models.skill import CandidateSkill
from app.services.matching.dto import CandidateEvidence


def build_candidate_evidence(
    profile: CandidateProfile,
    skills: list[CandidateSkill],
    experiences: list[Experience],
    educations: list[Education],
) -> CandidateEvidence:
    workplace = _normalize_list([profile.remote_preference] if profile.remote_preference else [])
    return CandidateEvidence(
        skills=[item.skill_name for item in skills],
        experiences=[
            {
                "company_name": item.company_name,
                "job_title": item.job_title,
                "start_date": item.start_date.isoformat(),
                "end_date": item.end_date.isoformat() if item.end_date else None,
                "description": item.description,
                "technologies": list(item.technologies or []),
                "achievements": list(item.achievements or []),
            }
            for item in experiences
        ],
        education=[
            {
                "institution": item.institution,
                "degree": item.degree,
                "field_of_study": item.field_of_study,
            }
            for item in educations
        ],
        total_years_experience=_years(profile, experiences),
        current_title=profile.current_role,
        preferred_locations=list(profile.preferred_locations or []),
        preferred_workplace_types=workplace,
        preferred_employment_types=_normalize_list(list(profile.preferred_job_types or [])),
        minimum_salary=_num(profile.minimum_salary),
        maximum_salary=_num(profile.maximum_salary),
        salary_currency=profile.salary_currency,
        headline=profile.headline,
        summary=profile.summary,
    )


def _years(profile: CandidateProfile, experiences: list[Experience]) -> int | None:
    if profile.years_experience is not None:
        return int(profile.years_experience)
    if not experiences:
        return None
    today = date.today()
    months = 0
    for item in experiences:
        end = item.end_date or today
        months += max((end.year - item.start_date.year) * 12 + (end.month - item.start_date.month), 0)
    return months // 12


def _num(value: Decimal | float | int | None) -> float | None:
    if value is None:
        return None
    return float(value)


def _normalize_list(values: list[str]) -> list[str]:
    return [value.strip().lower().replace("-", "_").replace(" ", "_") for value in values if value.strip()]
