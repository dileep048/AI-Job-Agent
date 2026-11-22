from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class NormalizedJob(BaseModel):
    external_id: str | None = None
    source_url: str | None = None
    title: str
    company_name: str
    company_url: str | None = None
    description: str | None = None
    location: str | None = None
    locations: list[str] = Field(default_factory=list)
    employment_type: str | None = None
    workplace_type: str | None = None
    salary_min: Decimal | None = None
    salary_max: Decimal | None = None
    salary_currency: str | None = None
    department: str | None = None
    experience_level: str | None = None
    posted_at: datetime | None = None
    expires_at: datetime | None = None
    is_active: bool = True
    skills: list[str] = Field(default_factory=list)
    raw_data: dict[str, Any] = Field(default_factory=dict)
