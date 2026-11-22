from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ProfileBase(BaseModel):
    headline: str | None = Field(default=None, max_length=255)
    summary: str | None = None
    years_experience: int | None = Field(default=None, ge=0, le=80)
    current_role: str | None = Field(default=None, max_length=255)
    current_company: str | None = Field(default=None, max_length=255)
    preferred_locations: list[str] = Field(default_factory=list)
    preferred_job_types: list[str] = Field(default_factory=list)
    minimum_salary: Decimal | None = Field(default=None, ge=0)
    maximum_salary: Decimal | None = Field(default=None, ge=0)
    salary_currency: str = Field(default="INR", max_length=8)
    remote_preference: str | None = Field(default=None, max_length=32)


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileResponse(ProfileBase, ORMModel):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
