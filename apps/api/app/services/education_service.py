from uuid import UUID

from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.education import Education
from app.repositories.education_repository import EducationRepository
from app.schemas.education import EducationCreate, EducationUpdate
from app.services.profile_service import ProfileService


class EducationService:
    def __init__(self, db: Session) -> None:
        self.educations = EducationRepository(db)
        self.profiles = ProfileService(db)

    def list(self, user_id: UUID) -> list[Education]:
        profile = self.profiles.get(user_id)
        return self.educations.list_by_profile(profile.id)

    def create(self, user_id: UUID, payload: EducationCreate) -> Education:
        profile = self.profiles.get(user_id)
        education = Education(profile_id=profile.id, **payload.model_dump())
        return self.educations.create(education)

    def update(self, user_id: UUID, education_id: UUID, payload: EducationUpdate) -> Education:
        profile = self.profiles.get(user_id)
        education = self.educations.get_by_id_and_profile(education_id, profile.id)
        if education is None:
            raise NotFoundError("EDUCATION_NOT_FOUND", "Education not found")
        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(education, field, value)
        return self.educations.save(education)

    def delete(self, user_id: UUID, education_id: UUID) -> None:
        profile = self.profiles.get(user_id)
        education = self.educations.get_by_id_and_profile(education_id, profile.id)
        if education is None:
            raise NotFoundError("EDUCATION_NOT_FOUND", "Education not found")
        self.educations.delete(education)
