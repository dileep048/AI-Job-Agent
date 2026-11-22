from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.job import Job
from app.models.job_match import JobMatch


class JobMatchRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_for_user_job(self, user_id: UUID, job_id: UUID) -> JobMatch | None:
        stmt = (
            select(JobMatch)
            .options(selectinload(JobMatch.job))
            .where(JobMatch.user_id == user_id, JobMatch.job_id == job_id)
        )
        return self.db.scalar(stmt)

    def get_for_profile_job(self, profile_id: UUID, job_id: UUID) -> JobMatch | None:
        stmt = (
            select(JobMatch)
            .options(selectinload(JobMatch.job))
            .where(JobMatch.profile_id == profile_id, JobMatch.job_id == job_id)
        )
        return self.db.scalar(stmt)

    def get_by_id_for_user(self, match_id: UUID, user_id: UUID) -> JobMatch | None:
        stmt = (
            select(JobMatch)
            .options(selectinload(JobMatch.job))
            .where(JobMatch.id == match_id, JobMatch.user_id == user_id)
        )
        return self.db.scalar(stmt)

    def list_for_user(
        self, user_id: UUID, *, page: int, page_size: int, min_score: float | None = None
    ) -> tuple[list[JobMatch], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        filters = [JobMatch.user_id == user_id]
        if min_score is not None:
            filters.append(JobMatch.overall_score >= min_score)
        total = int(
            self.db.scalar(select(func.count()).select_from(JobMatch).where(*filters)) or 0
        )
        stmt = (
            select(JobMatch)
            .options(selectinload(JobMatch.job))
            .where(*filters)
            .order_by(JobMatch.overall_score.desc(), JobMatch.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self.db.scalars(stmt).all()), total

    def scores_for_jobs(self, user_id: UUID, job_ids: list[UUID]) -> dict[UUID, JobMatch]:
        if not job_ids:
            return {}
        stmt = select(JobMatch).where(JobMatch.user_id == user_id, JobMatch.job_id.in_(job_ids))
        return {item.job_id: item for item in self.db.scalars(stmt).all()}

    def scores_for_profile_jobs(self, profile_id: UUID, job_ids: list[UUID]) -> dict[UUID, JobMatch]:
        if not job_ids:
            return {}
        stmt = select(JobMatch).where(
            JobMatch.profile_id == profile_id, JobMatch.job_id.in_(job_ids)
        )
        return {item.job_id: item for item in self.db.scalars(stmt).all()}

    def list_for_profile(
        self,
        profile_id: UUID,
        *,
        page: int,
        page_size: int,
        min_score: float | None = None,
        recommendation: str | None = None,
        company: str | None = None,
        location: str | None = None,
        workplace_type: str | None = None,
    ) -> tuple[list[JobMatch], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        filters = [JobMatch.profile_id == profile_id]
        needs_job = any([company, location, workplace_type])
        if min_score is not None:
            filters.append(JobMatch.overall_score >= min_score)
        if recommendation:
            filters.append(JobMatch.recommendation == recommendation.upper())
        if company:
            filters.append(Job.company_name.ilike(f"%{company.strip()}%"))
        if location:
            filters.append(Job.location.ilike(f"%{location.strip()}%"))
        if workplace_type:
            filters.append(Job.workplace_type == workplace_type.strip().lower())
        count_stmt = select(func.count()).select_from(JobMatch)
        list_stmt = select(JobMatch).options(selectinload(JobMatch.job))
        if needs_job:
            count_stmt = count_stmt.join(Job, JobMatch.job_id == Job.id)
            list_stmt = list_stmt.join(Job, JobMatch.job_id == Job.id)
        total = int(self.db.scalar(count_stmt.where(*filters)) or 0)
        stmt = (
            list_stmt.where(*filters)
            .order_by(JobMatch.overall_score.desc(), JobMatch.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self.db.scalars(stmt).unique().all()), total

    def stats_for_profile(self, profile_id: UUID) -> dict[str, float | int | None]:
        total = int(
            self.db.scalar(
                select(func.count()).select_from(JobMatch).where(JobMatch.profile_id == profile_id)
            )
            or 0
        )
        strong = int(
            self.db.scalar(
                select(func.count())
                .select_from(JobMatch)
                .where(JobMatch.profile_id == profile_id, JobMatch.overall_score >= 80)
            )
            or 0
        )
        potential = int(
            self.db.scalar(
                select(func.count())
                .select_from(JobMatch)
                .where(
                    JobMatch.profile_id == profile_id,
                    JobMatch.overall_score >= 65,
                    JobMatch.overall_score < 80,
                )
            )
            or 0
        )
        average = self.db.scalar(
            select(func.avg(JobMatch.overall_score)).where(JobMatch.profile_id == profile_id)
        )
        return {
            "total_matches": total,
            "strong_matches": strong,
            "potential_matches": potential,
            "average_score": float(average) if average is not None else None,
        }

    def save(self, match: JobMatch) -> JobMatch:
        self.db.add(match)
        self.db.commit()
        self.db.refresh(match)
        return match
