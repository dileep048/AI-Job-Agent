from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.skill import CandidateSkill


class SkillRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_profile(self, profile_id: UUID) -> list[CandidateSkill]:
        stmt = select(CandidateSkill).where(CandidateSkill.profile_id == profile_id)
        return list(self.db.scalars(stmt).all())

    def get_by_id_and_profile(self, skill_id: UUID, profile_id: UUID) -> CandidateSkill | None:
        stmt = select(CandidateSkill).where(
            CandidateSkill.id == skill_id,
            CandidateSkill.profile_id == profile_id,
        )
        return self.db.scalar(stmt)

    def get_by_name(self, profile_id: UUID, skill_name: str) -> CandidateSkill | None:
        stmt = select(CandidateSkill).where(
            CandidateSkill.profile_id == profile_id,
            CandidateSkill.skill_name == skill_name,
        )
        return self.db.scalar(stmt)

    def create(self, skill: CandidateSkill) -> CandidateSkill:
        self.db.add(skill)
        self.db.commit()
        self.db.refresh(skill)
        return skill

    def save(self, skill: CandidateSkill) -> CandidateSkill:
        self.db.add(skill)
        self.db.commit()
        self.db.refresh(skill)
        return skill

    def delete(self, skill: CandidateSkill) -> None:
        self.db.delete(skill)
        self.db.commit()
