from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SkillRequirement:
    name: str
    importance: str = "required"


@dataclass
class JobRequirements:
    required_skills: list[str] = field(default_factory=list)
    preferred_skills: list[str] = field(default_factory=list)
    minimum_years_experience: int | None = None
    required_job_titles: list[str] = field(default_factory=list)
    education_requirements: list[str] = field(default_factory=list)
    location_requirements: list[str] = field(default_factory=list)
    workplace_type: str | None = None
    employment_type: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    salary_currency: str | None = None
    title: str = ""

    @property
    def all_skills(self) -> list[str]:
        return self.required_skills + [
            skill for skill in self.preferred_skills if skill not in self.required_skills
        ]

    def as_dict(self) -> dict[str, Any]:
        return {
            "required_skills": self.required_skills,
            "preferred_skills": self.preferred_skills,
            "minimum_years_experience": self.minimum_years_experience,
            "required_job_titles": self.required_job_titles,
            "education_requirements": self.education_requirements,
            "location_requirements": self.location_requirements,
            "workplace_type": self.workplace_type,
            "employment_type": self.employment_type,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "salary_currency": self.salary_currency,
            "title": self.title,
        }


@dataclass
class CandidateEvidence:
    skills: list[str] = field(default_factory=list)
    experiences: list[dict[str, Any]] = field(default_factory=list)
    education: list[dict[str, Any]] = field(default_factory=list)
    total_years_experience: int | None = None
    current_title: str | None = None
    preferred_locations: list[str] = field(default_factory=list)
    preferred_workplace_types: list[str] = field(default_factory=list)
    preferred_employment_types: list[str] = field(default_factory=list)
    minimum_salary: float | None = None
    maximum_salary: float | None = None
    salary_currency: str | None = None
    headline: str | None = None
    summary: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "skills": self.skills,
            "experiences": self.experiences,
            "education": self.education,
            "total_years_experience": self.total_years_experience,
            "current_title": self.current_title,
            "preferred_locations": self.preferred_locations,
            "preferred_workplace_types": self.preferred_workplace_types,
            "preferred_employment_types": self.preferred_employment_types,
            "minimum_salary": self.minimum_salary,
            "maximum_salary": self.maximum_salary,
            "salary_currency": self.salary_currency,
            "headline": self.headline,
            "summary": self.summary,
        }


@dataclass
class HardFilterResult:
    passed: bool
    reasons: list[str] = field(default_factory=list)


@dataclass
class MatchResult:
    score: float
    recommendation: str
    confidence: float
    matched_skills: list[str]
    missing_skills: list[str]
    preferred_matched: list[str] = field(default_factory=list)
    skill_score: float = 0.0
    experience_score: float = 0.0
    title_score: float = 0.0
    location_score: float = 0.0
    workplace_score: float = 0.0
    employment_score: float = 0.0
    salary_score: float = 0.0
    semantic_score: float = 0.0
    strengths: list[str] = field(default_factory=list)
    concerns: list[str] = field(default_factory=list)
    hard_filter: HardFilterResult = field(default_factory=lambda: HardFilterResult(True))
    breakdown: dict[str, Any] = field(default_factory=dict)
    explanation: str = ""
    explanation_source: str = "rules"
    ai_reasoning: dict[str, Any] = field(default_factory=dict)
