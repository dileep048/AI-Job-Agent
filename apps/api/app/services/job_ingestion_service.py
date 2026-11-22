from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.exceptions import NotFoundError, ValidationAppError
from app.models.job import Job
from app.models.job_skill import JobSkill
from app.models.job_source import JobSource
from app.repositories.job_repository import JobRepository
from app.repositories.job_source_repository import JobSourceRepository
from app.services.jobs.dto import NormalizedJob
from app.services.jobs.normalizer import JobNormalizationService
from app.services.jobs.sources.base import JobSourceAdapter
from app.services.jobs.sources.registry import get_adapter
from app.services.jobs.url_parser import require_ats_url

logger = logging.getLogger("ai_job_agent")


@dataclass
class IngestionResult:
    source: str
    fetched: int = 0
    inserted: int = 0
    updated: int = 0
    duplicates: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)


class JobIngestionService:
    def __init__(
        self,
        db: Session,
        *,
        adapter: JobSourceAdapter | None = None,
        normalizer: JobNormalizationService | None = None,
    ) -> None:
        self.db = db
        self.jobs = JobRepository(db)
        self.sources = JobSourceRepository(db)
        self.adapter = adapter
        self.normalizer = normalizer or JobNormalizationService()

    def ingest(
        self,
        *,
        source_id: UUID | None = None,
        source_type: str | None = None,
        configuration: dict[str, Any] | None = None,
    ) -> IngestionResult:
        configuration = configuration or {}
        source = self._resolve_source(source_id, source_type, configuration)
        if not source.is_active:
            raise ValidationAppError("SOURCE_INACTIVE", "This job source is disabled")

        self.sources.record_fetch_datetimes(source)
        adapter = self.adapter or get_adapter(source.source_type)
        merged_config = {**(source.configuration or {}), **configuration}
        logger.info("ingestion started source=%s type=%s", source.name, source.source_type)

        try:
            raw_jobs = adapter.fetch_jobs(merged_config)
        except ValidationAppError:
            raise
        except Exception:
            logger.exception("ingestion fetch failed source=%s", source.source_type)
            raise ValidationAppError(
                "SOURCE_FETCH_FAILED", "Could not fetch jobs from the source"
            ) from None

        result = IngestionResult(source=source.source_type, fetched=len(raw_jobs))
        logger.info("ingestion fetched source=%s count=%s", source.source_type, result.fetched)

        for raw in raw_jobs:
            try:
                outcome = self._upsert(source, raw)
            except ValidationAppError as exc:
                result.failed += 1
                result.errors.append(exc.message)
                logger.info(
                    "ingestion job failed source=%s reason=%s",
                    source.source_type,
                    exc.code,
                )
                continue
            except Exception:
                result.failed += 1
                result.errors.append("Job could not be processed")
                logger.exception("ingestion job failed source=%s", source.source_type)
                continue
            if outcome == "inserted":
                result.inserted += 1
            elif outcome == "updated":
                result.updated += 1
            else:
                result.duplicates += 1

        logger.info(
            "ingestion completed source=%s inserted=%s updated=%s duplicates=%s failed=%s",
            source.source_type,
            result.inserted,
            result.updated,
            result.duplicates,
            result.failed,
        )
        return result

    def ingest_from_url(self, url: str) -> IngestionResult:
        parsed = require_ats_url(url)
        return self.ingest(
            source_type=parsed.source_type,
            configuration=parsed.ingest_configuration(),
        )

    def _resolve_source(
        self,
        source_id: UUID | None,
        source_type: str | None,
        configuration: dict[str, Any],
    ) -> JobSource:
        if source_id:
            source = self.sources.get_by_id(source_id)
            if source is None:
                raise NotFoundError("SOURCE_NOT_FOUND", "Job source not found")
            return source
        if not source_type:
            raise ValidationAppError("INVALID_SOURCE", "source_id or source_type is required")
        source_type = source_type.lower()
        key = _board_key(source_type, configuration)
        if key:
            existing = self.sources.get_by_type_and_key(source_type, key)
            if existing:
                return existing
        else:
            existing = self.sources.get_by_type(source_type)
            if existing:
                return existing
        stored = _persistent_config(source_type, configuration, key)
        source = JobSource(
            name=str(stored.get("company_name") or key or source_type.title())[:128],
            source_type=source_type,
            external_key=key,
            base_url=_base_url(source_type, key),
            configuration=stored,
            is_active=True,
        )
        return self.sources.create(source)

    def _upsert(self, source: JobSource, raw: dict[str, Any]) -> str:
        normalized = self.normalizer.normalize(raw)
        digest = self.normalizer.hash_for(normalized)
        existing = None
        if source.id and normalized.external_id:
            existing = self.jobs.get_by_source_external(source.id, normalized.external_id)
        if existing is None:
            existing = self.jobs.get_by_content_hash(digest)
        if existing is None:
            self._insert(source, normalized, digest)
            return "inserted"
        changed = self._apply_update(existing, normalized, digest)
        if changed:
            return "updated"
        return "duplicate"

    def _insert(self, source: JobSource, normalized: NormalizedJob, digest: str) -> Job:
        job = Job(
            source_id=source.id,
            external_id=normalized.external_id,
            content_hash=digest,
            **self._job_fields(normalized),
        )
        for name in normalized.skills:
            job.skills.append(JobSkill(skill_name=name))
        return self.jobs.create(job)

    def _apply_update(self, job: Job, normalized: NormalizedJob, digest: str) -> bool:
        before = (
            job.description,
            job.location,
            str(job.salary_min),
            str(job.salary_max),
            job.is_active,
            job.posted_at,
            job.expires_at,
            job.content_hash,
        )
        job.description = normalized.description
        job.location = normalized.location
        job.locations = normalized.locations
        job.salary_min = normalized.salary_min
        job.salary_max = normalized.salary_max
        job.salary_currency = normalized.salary_currency
        job.is_active = normalized.is_active
        job.posted_at = normalized.posted_at
        job.expires_at = normalized.expires_at
        job.raw_data = normalized.raw_data
        job.content_hash = digest
        job.employment_type = normalized.employment_type
        job.workplace_type = normalized.workplace_type
        job.source_url = normalized.source_url
        self.jobs.save(job)
        after = (
            job.description,
            job.location,
            str(job.salary_min),
            str(job.salary_max),
            job.is_active,
            job.posted_at,
            job.expires_at,
            job.content_hash,
        )
        return before != after

    def _job_fields(self, normalized: NormalizedJob) -> dict[str, Any]:
        return {
            "source_url": normalized.source_url,
            "title": normalized.title,
            "company_name": normalized.company_name,
            "company_url": normalized.company_url,
            "description": normalized.description,
            "location": normalized.location,
            "locations": normalized.locations,
            "employment_type": normalized.employment_type,
            "workplace_type": normalized.workplace_type,
            "salary_min": normalized.salary_min,
            "salary_max": normalized.salary_max,
            "salary_currency": normalized.salary_currency,
            "department": normalized.department,
            "experience_level": normalized.experience_level,
            "posted_at": normalized.posted_at,
            "expires_at": normalized.expires_at,
            "is_active": normalized.is_active,
            "raw_data": normalized.raw_data,
        }


def _board_key(source_type: str, configuration: dict[str, Any]) -> str | None:
    if source_type == "greenhouse":
        value = configuration.get("board_token") or configuration.get("token")
    elif source_type == "lever":
        value = configuration.get("site") or configuration.get("token")
    else:
        return None
    text = str(value or "").strip().lower()
    return text or None


def _persistent_config(
    source_type: str, configuration: dict[str, Any], key: str | None
) -> dict[str, Any]:
    company = configuration.get("company_name") or key
    if source_type == "greenhouse" and key:
        return {"board_token": key, "company_name": company}
    if source_type == "lever" and key:
        return {"site": key, "company_name": company}
    return {k: v for k, v in configuration.items() if k != "job_id"}


def _base_url(source_type: str, key: str | None) -> str | None:
    if not key:
        return None
    if source_type == "greenhouse":
        return f"https://boards.greenhouse.io/{key}"
    if source_type == "lever":
        return f"https://jobs.lever.co/{key}"
    return None
