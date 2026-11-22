from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ResumeData(BaseModel):
    summary: str = ""
    skills: list[Any] = Field(default_factory=list)
    experience: list[Any] = Field(default_factory=list)
    education: list[Any] = Field(default_factory=list)
    projects: list[Any] = Field(default_factory=list)


class ResumeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    resume_data: ResumeData = Field(default_factory=ResumeData)
    is_default: bool = False


class ResumeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    resume_data: ResumeData | None = None
    is_default: bool | None = None


class ResumeResponse(ORMModel):
    id: UUID
    user_id: UUID
    name: str
    version: int
    resume_data: dict[str, Any]
    file_url: str | None
    file_name: str | None
    file_type: str | None
    file_size: int | None
    is_default: bool
    status: str
    created_at: datetime
    updated_at: datetime
