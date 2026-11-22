from uuid import UUID

from sqlalchemy.orm import Session

from app.exceptions import ConflictError, NotFoundError
from app.models.profile import CandidateProfile
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfileCreate, ProfileUpdate


class ProfileService:
    def __init__(self, db: Session) -> None:
        self.profiles = ProfileRepository(db)

    def get(self, user_id: UUID) -> CandidateProfile:
        profile = self.profiles.get_by_user_id(user_id)
        if profile is None:
            raise NotFoundError("PROFILE_NOT_FOUND", "Candidate profile not found")
        return profile

    def get_or_none(self, user_id: UUID) -> CandidateProfile | None:
        return self.profiles.get_by_user_id(user_id)

    def create(self, user_id: UUID, payload: ProfileCreate) -> CandidateProfile:
        if self.profiles.get_by_user_id(user_id) is not None:
            raise ConflictError("PROFILE_EXISTS", "A profile already exists for this user")
        profile = CandidateProfile(user_id=user_id, **payload.model_dump())
        return self.profiles.create(profile)

    def update(self, user_id: UUID, payload: ProfileUpdate) -> CandidateProfile:
        profile = self.get(user_id)
        for field, value in payload.model_dump().items():
            setattr(profile, field, value)
        return self.profiles.save(profile)

    def delete(self, user_id: UUID) -> None:
        profile = self.get(user_id)
        self.profiles.delete(profile)
