from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.education import Education


class EducationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_profile(self, profile_id: UUID) -> list[Education]:
        stmt = (
            select(Education)
            .where(Education.profile_id == profile_id)
            .order_by(Education.start_date.desc().nulls_last())
        )
        return list(self.db.scalars(stmt).all())

    def get_by_id_and_profile(self, education_id: UUID, profile_id: UUID) -> Education | None:
        stmt = select(Education).where(
            Education.id == education_id,
            Education.profile_id == profile_id,
        )
        return self.db.scalar(stmt)

    def create(self, education: Education) -> Education:
        self.db.add(education)
        self.db.commit()
        self.db.refresh(education)
        return education

    def save(self, education: Education) -> Education:
        self.db.add(education)
        self.db.commit()
        self.db.refresh(education)
        return education

    def delete(self, education: Education) -> None:
        self.db.delete(education)
        self.db.commit()
