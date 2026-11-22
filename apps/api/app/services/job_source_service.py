from uuid import UUID

from sqlalchemy.orm import Session

from app.exceptions import NotFoundError, ValidationAppError
from app.models.job_source import JobSource
from app.repositories.job_source_repository import JobSourceRepository
from app.schemas.job import (
    IngestResponse,
    JobSourceCreate,
    JobSourceCreateResponse,
    JobSourceResponse,
    JobSourceUpdate,
)
from app.services.job_ingestion_service import JobIngestionService
from app.services.jobs.url_parser import ParsedAtsUrl, require_ats_url


class JobSourceService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.sources = JobSourceRepository(db)

    def list_sources(self) -> list[JobSourceResponse]:
        return [JobSourceResponse.model_validate(item) for item in self.sources.list_all()]

    def add_source(self, payload: JobSourceCreate) -> JobSourceCreateResponse:
        parsed = _resolve_board(payload)
        existing = self.sources.get_by_type_and_key(parsed.source_type, parsed.key)
        if existing:
            source = existing
            if payload.name:
                source.name = payload.name[:128]
                source = self.sources.save(source)
        else:
            source = self.sources.create(
                JobSource(
                    name=(payload.name or parsed.key)[:128],
                    source_type=parsed.source_type,
                    external_key=parsed.key,
                    base_url=parsed.base_url(),
                    configuration=parsed.source_configuration(),
                    is_active=True,
                )
            )
        ingest = None
        if payload.fetch_now:
            result = JobIngestionService(self.db).ingest(source_id=source.id)
            ingest = IngestResponse(
                source=result.source,
                fetched=result.fetched,
                inserted=result.inserted,
                updated=result.updated,
                duplicates=result.duplicates,
                failed=result.failed,
                errors=result.errors[:20],
            )
        response = JobSourceCreateResponse.model_validate(source)
        response.ingest = ingest
        return response

    def update(self, source_id: UUID, payload: JobSourceUpdate) -> JobSourceResponse:
        source = self.sources.get_by_id(source_id)
        if source is None:
            raise NotFoundError("SOURCE_NOT_FOUND", "Job source not found")
        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(source, field, value)
        return JobSourceResponse.model_validate(self.sources.save(source))


def _resolve_board(payload: JobSourceCreate) -> ParsedAtsUrl:
    url = (payload.url or "").strip()
    if url:
        parsed = require_ats_url(url)
        return ParsedAtsUrl(parsed.source_type, parsed.key, None, parsed.original_url)

    source_type = (payload.source_type or "").strip().lower()
    token = (payload.token or "").strip().lower()
    if source_type not in {"greenhouse", "lever"}:
        raise ValidationAppError(
            "INVALID_SOURCE",
            "Provide a Greenhouse or Lever board URL, or a source type and token",
        )
    if not token:
        raise ValidationAppError("INVALID_SOURCE_CONFIG", "A board token or site slug is required")
    return ParsedAtsUrl(source_type, token, None, "")
