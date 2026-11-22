from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CandidateProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "candidate_profiles"

    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    headline: Mapped[str | None] = mapped_column(String(255), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    years_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_role: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    preferred_locations: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    preferred_job_types: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    minimum_salary: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    maximum_salary: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    salary_currency: Mapped[str] = mapped_column(String(8), nullable=False, default="INR")
    remote_preference: Mapped[str | None] = mapped_column(String(32), nullable=True)

    user: Mapped["User"] = relationship(back_populates="profile")  # noqa: F821
    skills: Mapped[list["CandidateSkill"]] = relationship(  # noqa: F821
        back_populates="profile",
        cascade="all, delete-orphan",
    )
    experiences: Mapped[list["Experience"]] = relationship(  # noqa: F821
        back_populates="profile",
        cascade="all, delete-orphan",
    )
    educations: Mapped[list["Education"]] = relationship(  # noqa: F821
        back_populates="profile",
        cascade="all, delete-orphan",
    )
