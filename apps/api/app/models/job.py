from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Job(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_jobs_source_external_id"),
        Index("ix_jobs_title", "title"),
        Index("ix_jobs_company_name", "company_name"),
        Index("ix_jobs_location", "location"),
        Index("ix_jobs_workplace_type", "workplace_type"),
        Index("ix_jobs_employment_type", "employment_type"),
        Index("ix_jobs_posted_at", "posted_at"),
        Index("ix_jobs_is_active", "is_active"),
        Index("ix_jobs_source_id", "source_id"),
        Index("ix_jobs_external_id", "external_id"),
        Index("ix_jobs_content_hash", "content_hash"),
        Index("ix_jobs_is_active_posted_at", "is_active", "posted_at"),
    )

    source_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("job_sources.id", ondelete="SET NULL"),
        nullable=True,
    )
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    locations: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    employment_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    workplace_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    salary_min: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    salary_max: Mapped[float | None] = mapped_column(Numeric(14, 2), nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    experience_level: Mapped[str | None] = mapped_column(String(64), nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    raw_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    source: Mapped["JobSource | None"] = relationship(back_populates="jobs")  # noqa: F821
    skills: Mapped[list["JobSkill"]] = relationship(  # noqa: F821
        back_populates="job",
        cascade="all, delete-orphan",
    )
