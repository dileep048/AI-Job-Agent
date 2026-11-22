from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.job_fetch_run import JobFetchRun


class JobFetchRunRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_latest(self) -> JobFetchRun | None:
        stmt = select(JobFetchRun).order_by(JobFetchRun.current_fetch_datetime.desc()).limit(1)
        return self.db.scalar(stmt)

    def get_by_id(self, run_id: UUID) -> JobFetchRun | None:
        return self.db.get(JobFetchRun, run_id)

    def create(self, run: JobFetchRun) -> JobFetchRun:
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def save(self, run: JobFetchRun) -> JobFetchRun:
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run
