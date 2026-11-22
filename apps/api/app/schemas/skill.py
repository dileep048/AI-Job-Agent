from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class SkillCreate(BaseModel):
    skill_name: str = Field(min_length=1, max_length=128)
    skill_type: str | None = Field(default=None, max_length=64)
    years_experience: int | None = Field(default=None, ge=0, le=80)
    proficiency: str | None = Field(default=None, max_length=32)


class SkillUpdate(BaseModel):
    skill_name: str | None = Field(default=None, min_length=1, max_length=128)
    skill_type: str | None = Field(default=None, max_length=64)
    years_experience: int | None = Field(default=None, ge=0, le=80)
    proficiency: str | None = Field(default=None, max_length=32)


class SkillResponse(ORMModel):
    id: UUID
    profile_id: UUID
    skill_name: str
    skill_type: str | None
    years_experience: int | None
    proficiency: str | None
    created_at: datetime
    updated_at: datetime
