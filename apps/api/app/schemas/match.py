from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel
from app.schemas.job import JobListItem


class MatchScoreSummary(BaseModel):
    overall_score: float
    recommendation: str


class JobMatchResponse(ORMModel):
    id: UUID
    job_id: UUID
    profile_id: UUID | None = None
    score: float | None = None
    overall_score: float
    skill_score: float
    experience_score: float
    title_score: float = 0
    location_score: float
    workplace_score: float = 0
    employment_score: float = 0
    salary_score: float
    semantic_score: float
    recommendation: str
    confidence: float = 0
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    requirements: dict[str, Any] = Field(default_factory=dict)
    breakdown: dict[str, Any] = Field(default_factory=dict)
    structured_score: dict[str, Any] = Field(default_factory=dict)
    hard_filter_passed: bool = True
    hard_filter_reasons: list[str] = Field(default_factory=list)
    explanation: str
    explanation_source: str
    algorithm_version: str | None = None
    created_at: datetime
    updated_at: datetime
    job: JobListItem | None = None


class JobMatchListResponse(BaseModel):
    items: list[JobMatchResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class MatchJobsRequest(BaseModel):
    job_ids: list[UUID] = Field(default_factory=list, max_length=20)


class MatchRefreshRequest(BaseModel):
    limit: int = Field(default=50, ge=1, le=100)
