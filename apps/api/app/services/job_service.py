from math import ceil
from uuid import UUID

from sqlalchemy.orm import Session

from app.exceptions import NotFoundError
from app.models.job import Job
from app.models.job_skill import JobSkill
from app.repositories.job_match_repository import JobMatchRepository
from app.repositories.job_repository import JobRepository, JobSearchFilters
from app.repositories.job_source_repository import JobSourceRepository
from app.schemas.job import (
    JobCreate,
    JobListItem,
    JobListResponse,
    JobResponse,
    JobSkillResponse,
    JobUpdate,
)
from app.services.jobs.normalizer import (
    JobNormalizationService,
    html_to_plain_text,
    normalize_employment_type,
    normalize_workplace_type,
)


class JobService:
    def __init__(self, db: Session) -> None:
        self.jobs = JobRepository(db)
        self.sources = JobSourceRepository(db)
        self.matches = JobMatchRepository(db)
        self.normalizer = JobNormalizationService()

    def list_jobs(
        self,
        filters: JobSearchFilters,
        *,
        page: int,
        page_size: int,
        user_id: UUID | None = None,
    ) -> JobListResponse:
        if filters.workplace_type:
            filters.workplace_type = normalize_workplace_type(filters.workplace_type)
        if filters.employment_type:
            mapped = normalize_employment_type(filters.employment_type)
            filters.employment_type = mapped
        items, total = self.jobs.search(filters, page=page, page_size=page_size)
        total_pages = ceil(total / page_size) if total else 0
        scores = {}
        if user_id and items:
            scores = self.matches.scores_for_jobs(user_id, [item.id for item in items])
        listed: list[JobListItem] = []
        for item in items:
            row = JobListItem.model_validate(item)
            match = scores.get(item.id)
            if match is not None:
                row.match_score = float(match.overall_score)
                row.recommendation = match.recommendation
            listed.append(row)
        return JobListResponse(
            items=listed,
            page=max(page, 1),
            page_size=min(max(page_size, 1), 100),
            total=total,
            total_pages=total_pages,
        )

    def get(self, job_id: UUID) -> JobResponse:
        job = self.jobs.get_by_id(job_id)
        if job is None:
            raise NotFoundError("JOB_NOT_FOUND", "Job not found")
        return self._to_response(job)

    def create(self, payload: JobCreate) -> JobResponse:
        normalized = self.normalizer.normalize(payload.model_dump())
        digest = self.normalizer.hash_for(normalized)
        existing = self.jobs.get_by_content_hash(digest)
        if existing:
            self._apply_payload(existing, normalized, digest)
            return self._to_response(self.jobs.get_by_id(existing.id) or existing)
        job = Job(
            source_id=None,
            external_id=normalized.external_id,
            content_hash=digest,
            source_url=normalized.source_url,
            title=normalized.title,
            company_name=normalized.company_name,
            company_url=normalized.company_url,
            description=normalized.description,
            location=normalized.location,
            locations=normalized.locations,
            employment_type=normalized.employment_type,
            workplace_type=normalized.workplace_type,
            salary_min=normalized.salary_min,
            salary_max=normalized.salary_max,
            salary_currency=normalized.salary_currency,
            department=normalized.department,
            experience_level=normalized.experience_level,
            posted_at=normalized.posted_at,
            expires_at=normalized.expires_at,
            is_active=normalized.is_active,
            raw_data=normalized.raw_data,
        )
        for name in normalized.skills:
            job.skills.append(JobSkill(skill_name=name))
        job = self.jobs.create(job)
        return self._to_response(self.jobs.get_by_id(job.id) or job)

    def update(self, job_id: UUID, payload: JobUpdate) -> JobResponse:
        job = self.jobs.get_by_id(job_id)
        if job is None:
            raise NotFoundError("JOB_NOT_FOUND", "Job not found")
        data = payload.model_dump(exclude_unset=True)
        skills = data.pop("skills", None)
        merged = {
            "title": job.title,
            "company_name": job.company_name,
            "company_url": job.company_url,
            "source_url": job.source_url,
            "description": job.description,
            "location": job.location,
            "locations": job.locations,
            "employment_type": job.employment_type,
            "workplace_type": job.workplace_type,
            "salary_min": job.salary_min,
            "salary_max": job.salary_max,
            "salary_currency": job.salary_currency,
            "department": job.department,
            "experience_level": job.experience_level,
            "posted_at": job.posted_at,
            "expires_at": job.expires_at,
            "is_active": job.is_active,
            "raw_data": job.raw_data,
        }
        merged.update(data)
        normalized = self.normalizer.normalize(merged)
        digest = self.normalizer.hash_for(normalized)
        self._apply_payload(job, normalized, digest)
        if skills is not None:
            self.jobs.replace_skills(job, skills)
        refreshed = self.jobs.get_by_id(job.id)
        return self._to_response(refreshed or job)

    def delete(self, job_id: UUID) -> None:
        job = self.jobs.get_by_id(job_id)
        if job is None:
            raise NotFoundError("JOB_NOT_FOUND", "Job not found")
        self.jobs.delete(job)

    def _apply_payload(self, job: Job, normalized, digest: str) -> None:
        job.title = normalized.title
        job.company_name = normalized.company_name
        job.company_url = normalized.company_url
        job.source_url = normalized.source_url
        job.description = normalized.description
        job.location = normalized.location
        job.locations = normalized.locations
        job.employment_type = normalized.employment_type
        job.workplace_type = normalized.workplace_type
        job.salary_min = normalized.salary_min
        job.salary_max = normalized.salary_max
        job.salary_currency = normalized.salary_currency
        job.department = normalized.department
        job.experience_level = normalized.experience_level
        job.posted_at = normalized.posted_at
        job.expires_at = normalized.expires_at
        job.is_active = normalized.is_active
        job.raw_data = normalized.raw_data
        job.content_hash = digest
        self.jobs.save(job)

    def _to_response(self, job: Job) -> JobResponse:
        data = JobResponse.model_validate(job)
        data.description = html_to_plain_text(job.description)
        data.source_type = job.source.source_type if job.source else None
        data.source_name = job.source.name if job.source else None
        data.skills = [JobSkillResponse.model_validate(skill) for skill in job.skills]
        return data
