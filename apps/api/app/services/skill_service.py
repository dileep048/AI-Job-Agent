from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import ConflictError, NotFoundError
from app.models.skill import CandidateSkill
from app.repositories.skill_repository import SkillRepository
from app.schemas.skill import SkillCreate, SkillUpdate
from app.services.profile_service import ProfileService


class SkillService:
    def __init__(self, db: Session) -> None:
        self.skills = SkillRepository(db)
        self.profiles = ProfileService(db)

    def list(self, user_id: UUID) -> list[CandidateSkill]:
        profile = self.profiles.get(user_id)
        return self.skills.list_by_profile(profile.id)

    def create(self, user_id: UUID, payload: SkillCreate) -> CandidateSkill:
        profile = self.profiles.get(user_id)
        if self.skills.get_by_name(profile.id, payload.skill_name):
            raise ConflictError("SKILL_EXISTS", "This skill already exists on the profile")
        skill = CandidateSkill(profile_id=profile.id, **payload.model_dump())
        try:
            return self.skills.create(skill)
        except IntegrityError as exc:
            self.skills.db.rollback()
            raise ConflictError("SKILL_EXISTS", "This skill already exists on the profile") from exc

    def update(self, user_id: UUID, skill_id: UUID, payload: SkillUpdate) -> CandidateSkill:
        profile = self.profiles.get(user_id)
        skill = self.skills.get_by_id_and_profile(skill_id, profile.id)
        if skill is None:
            raise NotFoundError("SKILL_NOT_FOUND", "Skill not found")
        data = payload.model_dump(exclude_unset=True)
        if "skill_name" in data and data["skill_name"] != skill.skill_name:
            existing = self.skills.get_by_name(profile.id, data["skill_name"])
            if existing:
                raise ConflictError("SKILL_EXISTS", "This skill already exists on the profile")
        for field, value in data.items():
            setattr(skill, field, value)
        try:
            return self.skills.save(skill)
        except IntegrityError as exc:
            self.skills.db.rollback()
            raise ConflictError("SKILL_EXISTS", "This skill already exists on the profile") from exc

    def delete(self, user_id: UUID, skill_id: UUID) -> None:
        profile = self.profiles.get(user_id)
        skill = self.skills.get_by_id_and_profile(skill_id, profile.id)
        if skill is None:
            raise NotFoundError("SKILL_NOT_FOUND", "Skill not found")
        self.skills.delete(skill)
