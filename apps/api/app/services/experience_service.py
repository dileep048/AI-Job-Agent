from uuid import UUID

from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.experience import Experience
from app.repositories.experience_repository import ExperienceRepository
from app.schemas.experience import ExperienceCreate, ExperienceUpdate
from app.services.profile_service import ProfileService


class ExperienceService:
    def __init__(self, db: Session) -> None:
        self.experiences = ExperienceRepository(db)
        self.profiles = ProfileService(db)

    def list(self, user_id: UUID) -> list[Experience]:
        profile = self.profiles.get(user_id)
        return self.experiences.list_by_profile(profile.id)

    def create(self, user_id: UUID, payload: ExperienceCreate) -> Experience:
        profile = self.profiles.get(user_id)
        experience = Experience(profile_id=profile.id, **payload.model_dump())
        return self.experiences.create(experience)

    def update(self, user_id: UUID, experience_id: UUID, payload: ExperienceUpdate) -> Experience:
        profile = self.profiles.get(user_id)
        experience = self.experiences.get_by_id_and_profile(experience_id, profile.id)
        if experience is None:
            raise NotFoundError("EXPERIENCE_NOT_FOUND", "Experience not found")
        data = payload.model_dump(exclude_unset=True)
        currently_working = data.pop("currently_working", None)
        if currently_working:
            data["end_date"] = None
        for field, value in data.items():
            setattr(experience, field, value)
        return self.experiences.save(experience)

    def delete(self, user_id: UUID, experience_id: UUID) -> None:
        profile = self.profiles.get(user_id)
        experience = self.experiences.get_by_id_and_profile(experience_id, profile.id)
        if experience is None:
            raise NotFoundError("EXPERIENCE_NOT_FOUND", "Experience not found")
        self.experiences.delete(experience)
