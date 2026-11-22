from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class JobSkillResponse(ORMModel):
    id: UUID
    skill_name: str
    skill_type: str | None


class JobCreate(BaseModel):
    title: str = Field(min_length=1, max_length=512)
    company_name: str = Field(min_length=1, max_length=255)
    company_url: str | None = Field(default=None, max_length=1024)
    source_url: str | None = Field(default=None, max_length=2048)
    description: str | None = None
    location: str | None = Field(default=None, max_length=255)
    locations: list[str] = Field(default_factory=list)
    employment_type: str | None = Field(default=None, max_length=64)
    workplace_type: str | None = Field(default=None, max_length=64)
    salary_min: Decimal | None = Field(default=None, ge=0)
    salary_max: Decimal | None = Field(default=None, ge=0)
    salary_currency: str | None = Field(default=None, max_length=8)
    department: str | None = Field(default=None, max_length=255)
    experience_level: str | None = Field(default=None, max_length=64)
    posted_at: datetime | None = None
    expires_at: datetime | None = None
    is_active: bool = True
    external_id: str | None = Field(default=None, max_length=255)
    skills: list[str] = Field(default_factory=list)
    raw_data: dict[str, Any] = Field(default_factory=dict)


class JobUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=512)
    company_name: str | None = Field(default=None, min_length=1, max_length=255)
    company_url: str | None = Field(default=None, max_length=1024)
    source_url: str | None = Field(default=None, max_length=2048)
    description: str | None = None
    location: str | None = Field(default=None, max_length=255)
    locations: list[str] | None = None
    employment_type: str | None = Field(default=None, max_length=64)
    workplace_type: str | None = Field(default=None, max_length=64)
    salary_min: Decimal | None = Field(default=None, ge=0)
    salary_max: Decimal | None = Field(default=None, ge=0)
    salary_currency: str | None = Field(default=None, max_length=8)
    department: str | None = Field(default=None, max_length=255)
    experience_level: str | None = Field(default=None, max_length=64)
    posted_at: datetime | None = None
    expires_at: datetime | None = None
    is_active: bool | None = None
    skills: list[str] | None = None


class JobListItem(ORMModel):
    id: UUID
    title: str
    company_name: str
    location: str | None
    workplace_type: str | None
    employment_type: str | None
    salary_min: Decimal | None
    salary_max: Decimal | None
    salary_currency: str | None
    posted_at: datetime | None
    is_active: bool
    source_url: str | None
    experience_level: str | None
    created_at: datetime
    updated_at: datetime
    match_score: float | None = None
    recommendation: str | None = None


class JobResponse(JobListItem):
    company_url: str | None
    description: str | None
    locations: list
    department: str | None
    expires_at: datetime | None
    external_id: str | None
    source_id: UUID | None
    source_type: str | None = None
    source_name: str | None = None
    skills: list[JobSkillResponse] = Field(default_factory=list)


class JobListResponse(BaseModel):
    items: list[JobListItem]
    page: int
    page_size: int
    total: int
    total_pages: int


class IngestRequest(BaseModel):
    source_id: UUID | None = None
    source_type: str | None = Field(default=None, max_length=64)
    configuration: dict[str, Any] = Field(default_factory=dict)
    url: str | None = Field(default=None, max_length=2048)


class JobUrlImportRequest(BaseModel):
    url: str = Field(min_length=8, max_length=2048)


class IngestResponse(BaseModel):
    source: str
    fetched: int
    inserted: int
    updated: int
    duplicates: int
    failed: int
    errors: list[str] = Field(default_factory=list)


class JobSourceResponse(ORMModel):
    id: UUID
    name: str
    source_type: str
    external_key: str | None = None
    base_url: str | None
    is_active: bool
    current_fetch_datetime: datetime | None = None
    last_fetch_datetime: datetime | None = None
    created_at: datetime
    updated_at: datetime


class JobSourceUpdate(BaseModel):
    is_active: bool | None = None
    name: str | None = Field(default=None, max_length=128)


class JobSourceCreate(BaseModel):
    url: str | None = Field(default=None, max_length=2048)
    source_type: str | None = Field(default=None, max_length=64)
    token: str | None = Field(default=None, max_length=128)
    name: str | None = Field(default=None, max_length=128)
    fetch_now: bool = True


class JobSourceCreateResponse(JobSourceResponse):
    ingest: IngestResponse | None = None


class JobFetchRunResponse(ORMModel):
    id: UUID
    current_fetch_datetime: datetime
    last_fetch_datetime: datetime | None
    finished_at: datetime | None
    status: str
    boards_attempted: int
    boards_succeeded: int
    fetched: int
    inserted: int
    updated: int
    duplicates: int
    failed: int
    errors: list[str] = Field(default_factory=list)
