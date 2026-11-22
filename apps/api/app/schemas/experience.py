from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import ORMModel


class ExperienceCreate(BaseModel):
    company_name: str = Field(min_length=1, max_length=255)
    job_title: str = Field(min_length=1, max_length=255)
    start_date: date
    end_date: date | None = None
    description: str | None = None
    achievements: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_dates(self) -> "ExperienceCreate":
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")
        return self


class ExperienceUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=1, max_length=255)
    job_title: str | None = Field(default=None, min_length=1, max_length=255)
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None
    achievements: list[str] | None = None
    technologies: list[str] | None = None
    currently_working: bool | None = None


class ExperienceResponse(ORMModel):
    id: UUID
    profile_id: UUID
    company_name: str
    job_title: str
    start_date: date
    end_date: date | None
    description: str | None
    achievements: list[str]
    technologies: list[str]
    created_at: datetime
    updated_at: datetime
