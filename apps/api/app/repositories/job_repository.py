from uuid import UUID

from sqlalchemy import Select, String, cast, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.job import Job
from app.models.job_skill import JobSkill
from app.models.job_source import JobSource


class JobSearchFilters:
    def __init__(
        self,
        *,
        q: str | None = None,
        location: str | None = None,
        workplace_type: str | None = None,
        employment_type: str | None = None,
        company: str | None = None,
        experience_level: str | None = None,
        salary_min: float | None = None,
        salary_max: float | None = None,
        is_active: bool | None = True,
        source: str | None = None,
    ) -> None:
        self.q = q
        self.location = location
        self.workplace_type = workplace_type
        self.employment_type = employment_type
        self.company = company
        self.experience_level = experience_level
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.is_active = is_active
        self.source = source


class JobRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, job_id: UUID) -> Job | None:
        stmt = (
            select(Job)
            .options(selectinload(Job.skills), selectinload(Job.source))
            .where(Job.id == job_id)
        )
        return self.db.scalar(stmt)

    def get_by_source_external(self, source_id: UUID, external_id: str) -> Job | None:
        stmt = select(Job).where(Job.source_id == source_id, Job.external_id == external_id)
        return self.db.scalar(stmt)

    def get_by_content_hash(self, content_hash: str) -> Job | None:
        stmt = select(Job).where(Job.content_hash == content_hash).limit(1)
        return self.db.scalar(stmt)

    def create(self, job: Job) -> Job:
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def save(self, job: Job) -> Job:
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def delete(self, job: Job) -> None:
        self.db.delete(job)
        self.db.commit()

    def replace_skills(self, job: Job, skill_names: list[str]) -> None:
        job.skills.clear()
        seen: set[str] = set()
        for name in skill_names:
            key = name.strip()
            if not key or key.lower() in seen:
                continue
            seen.add(key.lower())
            job.skills.append(JobSkill(skill_name=key))
        self.save(job)

    def _apply_filters(self, stmt: Select, filters: JobSearchFilters) -> Select:
        if filters.q:
            pattern = f"%{filters.q.strip()}%"
            stmt = stmt.where(
                or_(
                    Job.title.ilike(pattern),
                    Job.company_name.ilike(pattern),
                    Job.description.ilike(pattern),
                    Job.location.ilike(pattern),
                    cast(Job.locations, String).ilike(pattern),
                )
            )
        if filters.location:
            pattern = f"%{filters.location.strip()}%"
            stmt = stmt.where(
                or_(
                    Job.location.ilike(pattern),
                    cast(Job.locations, String).ilike(pattern),
                )
            )
        if filters.workplace_type:
            workplace = filters.workplace_type.strip().lower()
            workplace_match = [func.lower(Job.workplace_type) == workplace]
            if workplace == "remote":
                workplace_match.extend(
                    [
                        Job.location.ilike("%remote%"),
                        cast(Job.locations, String).ilike("%remote%"),
                    ]
                )
            stmt = stmt.where(or_(*workplace_match))
        if filters.employment_type:
            employment = (
                filters.employment_type.strip().lower().replace("-", "_").replace(" ", "_")
            )
            stmt = stmt.where(func.lower(Job.employment_type) == employment)
        if filters.company:
            stmt = stmt.where(Job.company_name.ilike(f"%{filters.company.strip()}%"))
        if filters.experience_level:
            stmt = stmt.where(Job.experience_level.ilike(f"%{filters.experience_level.strip()}%"))
        if filters.salary_min is not None:
            stmt = stmt.where(Job.salary_min >= filters.salary_min)
        if filters.salary_max is not None:
            stmt = stmt.where(Job.salary_max <= filters.salary_max)
        if filters.is_active is not None:
            stmt = stmt.where(Job.is_active == filters.is_active)
        if filters.source:
            stmt = stmt.join(JobSource, Job.source_id == JobSource.id, isouter=True).where(
                JobSource.source_type == filters.source
            )
        return stmt

    def search(
        self, filters: JobSearchFilters, *, page: int, page_size: int
    ) -> tuple[list[Job], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        base = self._apply_filters(select(Job), filters)
        total = int(self.db.scalar(select(func.count()).select_from(base.subquery())) or 0)
        stmt = (
            self._apply_filters(select(Job), filters)
            .options(selectinload(Job.skills), selectinload(Job.source))
            .order_by(Job.posted_at.desc().nulls_last(), Job.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self.db.scalars(stmt).unique().all()), total
