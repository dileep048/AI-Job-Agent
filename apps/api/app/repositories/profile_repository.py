from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.profile import CandidateProfile


class ProfileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_user_id(self, user_id: UUID) -> CandidateProfile | None:
        stmt = select(CandidateProfile).where(CandidateProfile.user_id == user_id)
        return self.db.scalar(stmt)

    def create(self, profile: CandidateProfile) -> CandidateProfile:
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def save(self, profile: CandidateProfile) -> CandidateProfile:
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def delete(self, profile: CandidateProfile) -> None:
        self.db.delete(profile)
        self.db.commit()
