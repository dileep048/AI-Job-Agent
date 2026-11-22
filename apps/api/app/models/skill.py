from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CandidateSkill(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "candidate_skills"
    __table_args__ = (
        UniqueConstraint("profile_id", "skill_name", name="uq_candidate_skills_profile_name"),
    )

    profile_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    skill_name: Mapped[str] = mapped_column(String(128), nullable=False)
    skill_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    years_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    proficiency: Mapped[str | None] = mapped_column(String(32), nullable=True)

    profile: Mapped["CandidateProfile"] = relationship(back_populates="skills")  # noqa: F821
