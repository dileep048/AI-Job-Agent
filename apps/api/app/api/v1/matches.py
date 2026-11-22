from fastapi import APIRouter, Query

from app.schemas.match import (
    JobMatchListResponse,
    JobMatchResponse,
    MatchJobsRequest,
    MatchRefreshRequest,
)
from app.security.dependencies import CurrentUser, DbSession
from app.services.matching_service import MatchingService

router = APIRouter(tags=["matches"])


@router.get("/matches", response_model=JobMatchListResponse)
def list_matches(
    current_user: CurrentUser,
    db: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    min_score: float | None = Query(default=None, ge=0, le=100),
) -> JobMatchListResponse:
    return MatchingService(db).list_matches(
        current_user.id, page=page, page_size=page_size, min_score=min_score
    )


@router.post("/matches/jobs", response_model=list[JobMatchResponse])
def score_jobs(
    payload: MatchJobsRequest, current_user: CurrentUser, db: DbSession
) -> list[JobMatchResponse]:
    return MatchingService(db).score_jobs(current_user.id, payload.job_ids)


@router.post("/matches/refresh", response_model=list[JobMatchResponse])
def refresh_matches(
    payload: MatchRefreshRequest, current_user: CurrentUser, db: DbSession
) -> list[JobMatchResponse]:
    return MatchingService(db).score_latest(current_user.id, limit=payload.limit)
