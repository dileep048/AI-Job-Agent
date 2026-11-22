from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.experience import Experience


class ExperienceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_profile(self, profile_id: UUID) -> list[Experience]:
        stmt = (
            select(Experience)
            .where(Experience.profile_id == profile_id)
            .order_by(Experience.start_date.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id_and_profile(self, experience_id: UUID, profile_id: UUID) -> Experience | None:
        stmt = select(Experience).where(
            Experience.id == experience_id,
            Experience.profile_id == profile_id,
        )
        return self.db.scalar(stmt)

    def create(self, experience: Experience) -> Experience:
        self.db.add(experience)
        self.db.commit()
        self.db.refresh(experience)
        return experience

    def save(self, experience: Experience) -> Experience:
        self.db.add(experience)
        self.db.commit()
        self.db.refresh(experience)
        return experience

    def delete(self, experience: Experience) -> None:
        self.db.delete(experience)
        self.db.commit()
