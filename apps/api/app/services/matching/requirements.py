from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from app.services.matching.catalog import KNOWN_SKILLS
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


@dataclass
class JobRequirements:
    skills: list[str] = field(default_factory=list)
    years_required: int | None = None
    experience_level: str | None = None
    locations: list[str] = field(default_factory=list)
    workplace_type: str | None = None
    employment_type: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str | None = None
    title: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "skills": self.skills,
            "years_required": self.years_required,
            "experience_level": self.experience_level,
            "locations": self.locations,
            "workplace_type": self.workplace_type,
            "employment_type": self.employment_type,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "salary_currency": self.salary_currency,
            "title": self.title,
        }


def extract_requirements(
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
    extra_skills: list[str] | None = None,
) -> JobRequirements:
    text = f"{title}\n{description or ''}"
    skills = _unique_skills(
        [*structured_skills, *_skills_from_text(text), *(extra_skills or [])]
    )
    years = _years_from_text(text)
    if years is None:
        years = _years_from_level(experience_level)
    loc_list = [item for item in (locations or []) if item]
    if location and location not in loc_list:
        loc_list = [location, *loc_list]
    return JobRequirements(
        skills=skills,
        years_required=years,
        experience_level=experience_level,
        locations=loc_list,
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
    return ordered[:40]


def _skills_from_text(text: str) -> list[str]:
    lowered = text.lower()
    found: list[str] = []
    for skill in KNOWN_SKILLS:
        if skill in lowered:
            found.append(skill)
    return found


def _years_from_text(text: str) -> int | None:
    match = _YEARS.search(text) or _YEARS_SHORT.search(text)
    if not match:
        return None
    return int(match.group(1))


def _years_from_level(level: str | None) -> int | None:
    if not level:
        return None
    key = level.strip().lower().replace("-", " ")
    for name, years in _LEVELS.items():
        if name in key:
            return years
    return None
