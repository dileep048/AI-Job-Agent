from __future__ import annotations

import re

from app.services.matching.catalog import KNOWN_SKILLS
from app.services.matching.dto import JobRequirements
from app.services.matching.llm import extract_requirements_with_llm
from app.services.matching.skills import normalize_skill

_YEARS = re.compile(
    r"(?:at least\s+)?(\d+)\s*(?:\+|plus)?\s*(?:-\s*(\d+)\s*)?(?:years?|yrs?)\s+"
    r"(?:of\s+)?(?:experience|exp)?",
    re.IGNORECASE,
)
_YEARS_SHORT = re.compile(r"(\d+)\+\s*(?:years?|yrs?)", re.IGNORECASE)
_LEVELS = {
    "intern": 0,
    "internship": 0,
    "entry": 1,
    "junior": 1,
    "associate": 2,
    "mid": 3,
    "intermediate": 3,
    "senior": 5,
    "staff": 8,
    "principal": 10,
    "lead": 7,
    "director": 12,
}


def extract_job_requirements(
    *,
    title: str,
    description: str | None,
    structured_skills: list[str],
    location: str | None,
    locations: list[str] | None,
    workplace_type: str | None,
    employment_type: str | None,
    experience_level: str | None,
    salary_min: float | None,
    salary_max: float | None,
    salary_currency: str | None,
    use_llm: bool = True,
) -> JobRequirements:
    text = f"{title}\n{description or ''}"
    required = _unique_skills([*structured_skills, *_skills_from_text(text)])
    preferred: list[str] = []
    llm_required: list[str] = []
    llm_preferred: list[str] = []
    if use_llm:
        llm = extract_requirements_with_llm(title, description)
        llm_required = llm.required_skills
        llm_preferred = llm.preferred_skills
        for skill in llm_required:
            if skill not in required:
                required.append(skill)
        preferred = [skill for skill in llm_preferred if skill not in required]
    years = _years_from_text(text) or _years_from_level(experience_level)
    locs = [item for item in (locations or []) if item]
    if location and location not in locs:
        locs = [location, *locs]
    return JobRequirements(
        required_skills=required[:40],
        preferred_skills=preferred[:20],
        minimum_years_experience=years,
        required_job_titles=[title] if title else [],
        location_requirements=locs,
        workplace_type=workplace_type,
        employment_type=employment_type,
        salary_min=salary_min,
        salary_max=salary_max,
        salary_currency=salary_currency,
        title=title,
    )


def _unique_skills(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        key = normalize_skill(value)
        if not key or key in seen or len(key) < 2:
            continue
        seen.add(key)
        ordered.append(value.strip())
    return ordered


def _skills_from_text(text: str) -> list[str]:
    lowered = text.lower()
    return [skill for skill in KNOWN_SKILLS if skill in lowered]


def _years_from_text(text: str) -> int | None:
    match = _YEARS.search(text) or _YEARS_SHORT.search(text)
    return int(match.group(1)) if match else None


def _years_from_level(level: str | None) -> int | None:
    if not level:
        return None
    key = level.strip().lower().replace("-", " ")
    for name, years in _LEVELS.items():
        if name in key:
            return years
    return None
