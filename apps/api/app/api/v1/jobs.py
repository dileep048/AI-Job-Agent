from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from app.exceptions import ConflictError
from app.repositories.job_repository import JobSearchFilters
from app.schemas.job import (
    IngestRequest,
    IngestResponse,
    JobCreate,
    JobFetchRunResponse,
    JobListResponse,
    JobResponse,
    JobSourceCreate,
    JobSourceCreateResponse,
    JobSourceResponse,
    JobSourceUpdate,
    JobUpdate,
    JobUrlImportRequest,
)
from app.schemas.match import JobMatchResponse
from app.security.dependencies import CurrentUser, DbSession
from app.services.job_ingestion_service import JobIngestionService
from app.services.job_service import JobService
from app.services.job_source_service import JobSourceService
from app.services.matching_service import MatchingService
from app.services.scheduled_ingestion_service import ScheduledIngestionService

router = APIRouter(tags=["jobs"])


@router.get("/jobs", response_model=JobListResponse)
def list_jobs(
    current_user: CurrentUser,
    db: DbSession,
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
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> JobListResponse:
    filters = JobSearchFilters(
        q=q,
        location=location,
        workplace_type=workplace_type,
        employment_type=employment_type,
        company=company,
        experience_level=experience_level,
        salary_min=salary_min,
        salary_max=salary_max,
        is_active=is_active,
        source=source,
    )
    return JobService(db).list_jobs(
        filters, page=page, page_size=page_size, user_id=current_user.id
    )


@router.post("/jobs", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate, current_user: CurrentUser, db: DbSession) -> JobResponse:
    del current_user
    return JobService(db).create(payload)


@router.post("/jobs/ingest", response_model=IngestResponse)
def ingest_jobs(payload: IngestRequest, current_user: CurrentUser, db: DbSession) -> IngestResponse:
    del current_user
    service = JobIngestionService(db)
    if payload.url:
        result = service.ingest_from_url(payload.url)
    else:
        result = service.ingest(
            source_id=payload.source_id,
            source_type=payload.source_type,
            configuration=payload.configuration,
        )
    return IngestResponse(
        source=result.source,
        fetched=result.fetched,
        inserted=result.inserted,
        updated=result.updated,
        duplicates=result.duplicates,
        failed=result.failed,
        errors=result.errors[:20],
    )


@router.post("/jobs/from-url", response_model=IngestResponse)
def import_job_from_url(
    payload: JobUrlImportRequest, current_user: CurrentUser, db: DbSession
) -> IngestResponse:
    del current_user
    result = JobIngestionService(db).ingest_from_url(payload.url)
    return IngestResponse(
        source=result.source,
        fetched=result.fetched,
        inserted=result.inserted,
        updated=result.updated,
        duplicates=result.duplicates,
        failed=result.failed,
        errors=result.errors[:20],
    )


@router.post("/jobs/ingest/boards", response_model=JobFetchRunResponse)
def ingest_greenhouse_and_lever(
    current_user: CurrentUser, db: DbSession
) -> JobFetchRunResponse:
    del current_user
    run = ScheduledIngestionService(db).ingest_greenhouse_and_lever()
    if run is None:
        raise ConflictError(
            "INGEST_IN_PROGRESS",
            "A Greenhouse/Lever fetch is already running",
        )
    return JobFetchRunResponse.model_validate(run)


@router.get("/jobs/fetch-runs/latest", response_model=JobFetchRunResponse | None)
def latest_fetch_run(current_user: CurrentUser, db: DbSession) -> JobFetchRunResponse | None:
    del current_user
    run = ScheduledIngestionService(db).latest_run()
    if run is None:
        return None
    return JobFetchRunResponse.model_validate(run)


@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: UUID, current_user: CurrentUser, db: DbSession) -> JobResponse:
    del current_user
    return JobService(db).get(job_id)


@router.post("/jobs/{job_id}/match", response_model=JobMatchResponse)
def score_job(job_id: UUID, current_user: CurrentUser, db: DbSession) -> JobMatchResponse:
    return MatchingService(db).score_job(current_user.id, job_id)


@router.get("/jobs/{job_id}/match", response_model=JobMatchResponse)
def get_job_match(job_id: UUID, current_user: CurrentUser, db: DbSession) -> JobMatchResponse:
    return MatchingService(db).get(current_user.id, job_id)


@router.patch("/jobs/{job_id}", response_model=JobResponse)
def update_job(
    job_id: UUID, payload: JobUpdate, current_user: CurrentUser, db: DbSession
) -> JobResponse:
    del current_user
    return JobService(db).update(job_id, payload)


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: UUID, current_user: CurrentUser, db: DbSession) -> Response:
    del current_user
    JobService(db).delete(job_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/job-sources", response_model=list[JobSourceResponse])
def list_sources(current_user: CurrentUser, db: DbSession) -> list[JobSourceResponse]:
    del current_user
    return JobSourceService(db).list_sources()


@router.post("/job-sources", response_model=JobSourceCreateResponse)
def create_source(
    payload: JobSourceCreate, current_user: CurrentUser, db: DbSession
) -> JobSourceCreateResponse:
    del current_user
    return JobSourceService(db).add_source(payload)


@router.patch("/job-sources/{source_id}", response_model=JobSourceResponse)
def update_source(
    source_id: UUID, payload: JobSourceUpdate, current_user: CurrentUser, db: DbSession
) -> JobSourceResponse:
    del current_user
    return JobSourceService(db).update(source_id, payload)
