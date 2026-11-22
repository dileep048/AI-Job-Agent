from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job_source import JobSource


class JobSourceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, source_id: UUID) -> JobSource | None:
        return self.db.get(JobSource, source_id)

    def get_by_type(self, source_type: str) -> JobSource | None:
        stmt = select(JobSource).where(JobSource.source_type == source_type).limit(1)
        return self.db.scalar(stmt)

    def get_by_type_and_key(self, source_type: str, external_key: str) -> JobSource | None:
        stmt = select(JobSource).where(
            JobSource.source_type == source_type,
            JobSource.external_key == external_key,
        )
        return self.db.scalar(stmt)

    def list_all(self) -> list[JobSource]:
        stmt = select(JobSource).order_by(JobSource.name)
        return list(self.db.scalars(stmt).all())

    def list_active_boards(
        self, source_types: tuple[str, ...] = ("greenhouse", "lever")
    ) -> list[JobSource]:
        stmt = (
            select(JobSource)
            .where(JobSource.is_active.is_(True), JobSource.source_type.in_(source_types))
            .order_by(JobSource.source_type, JobSource.name)
        )
        return list(self.db.scalars(stmt).all())

    def create(self, source: JobSource) -> JobSource:
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def save(self, source: JobSource) -> JobSource:
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def record_fetch_datetimes(
        self, source: JobSource, fetched_at: datetime | None = None
    ) -> JobSource:
        now = fetched_at or datetime.now(UTC)
        source.last_fetch_datetime = source.current_fetch_datetime
        source.current_fetch_datetime = now
        return self.save(source)
