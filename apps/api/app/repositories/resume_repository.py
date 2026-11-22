from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.resume import Resume


class ResumeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_user(self, user_id: UUID) -> list[Resume]:
        stmt = select(Resume).where(Resume.user_id == user_id).order_by(Resume.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def get_by_id_and_user(self, resume_id: UUID, user_id: UUID) -> Resume | None:
        stmt = select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id)
        return self.db.scalar(stmt)

    def create(self, resume: Resume) -> Resume:
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def save(self, resume: Resume) -> Resume:
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def delete(self, resume: Resume) -> None:
        self.db.delete(resume)
        self.db.commit()

    def clear_defaults(self, user_id: UUID, except_id: UUID | None = None) -> None:
        stmt = update(Resume).where(Resume.user_id == user_id, Resume.is_default.is_(True))
        if except_id is not None:
            stmt = stmt.where(Resume.id != except_id)
        self.db.execute(stmt.values(is_default=False))
        self.db.commit()

    def count_by_user(self, user_id: UUID) -> int:
        from sqlalchemy import func

        stmt = select(func.count()).select_from(Resume).where(Resume.user_id == user_id)
        return int(self.db.scalar(stmt) or 0)
