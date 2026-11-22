from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class JobMatch(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "job_matches"
    __table_args__ = (
        UniqueConstraint("profile_id", "job_id", name="uq_job_matches_profile_job"),
        Index("ix_job_matches_user_id", "user_id"),
        Index("ix_job_matches_profile_id", "profile_id"),
        Index("ix_job_matches_job_id", "job_id"),
        Index("ix_job_matches_user_score", "user_id", "overall_score"),
        Index("ix_job_matches_profile_score", "profile_id", "overall_score"),
    )

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    profile_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    job_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    overall_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    skill_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    experience_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    title_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    location_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    workplace_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    employment_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=0)
    salary_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    semantic_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    recommendation: Mapped[str] = mapped_column(String(32), nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False, default=0)
    matched_skills: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    missing_skills: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    strengths: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    concerns: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    requirements: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    candidate_evidence: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    structured_score: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    breakdown: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    ai_reasoning: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    explanation_source: Mapped[str] = mapped_column(String(16), nullable=False, default="rules")
    hard_filter_passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    hard_filter_reasons: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    inputs_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    algorithm_version: Mapped[str] = mapped_column(String(32), nullable=False, default="s3.0.0")
    model_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(64), nullable=True)

    job: Mapped["Job"] = relationship()  # noqa: F821
