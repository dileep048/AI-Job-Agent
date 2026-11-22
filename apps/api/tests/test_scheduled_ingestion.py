from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.conftest import auth_header

from app.config.settings import get_settings
from app.models.job import Job
from app.services.jobs.board_catalog import BoardRef
from app.services.scheduled_ingestion_service import ScheduledIngestionService


def _gh_response() -> Mock:
    response = Mock(status_code=200)
    response.json.return_value = {
        "jobs": [
            {
                "id": 1,
                "title": "Backend Engineer",
                "absolute_url": "https://example.com/gh",
                "content": "Build APIs",
                "location": {"name": "Remote"},
                "departments": [],
                "offices": [],
            }
        ]
    }
    return response


def _lever_response() -> Mock:
    response = Mock(status_code=200)
    response.json.return_value = [
        {
            "id": "lev-1",
            "text": "Product Designer",
            "hostedUrl": "https://example.com/lever",
            "descriptionPlain": "Design systems",
            "categories": {"location": "NYC", "commitment": "full-time"},
        }
    ]
    return response


def _http_get(url: str, **kwargs: object) -> Mock:
    if "greenhouse.io" in url:
        return _gh_response()
    return _lever_response()


def test_scheduled_ingest_stores_jobs_and_fetch_datetimes(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("JOB_INGEST_BOARD_DELAY_SECONDS", "0")
    get_settings.cache_clear()
    boards = [
        BoardRef("greenhouse", "acme", "Acme"),
        BoardRef("lever", "globex", "Globex"),
    ]
    with (
        patch("app.services.jobs.sources.greenhouse.httpx.get", side_effect=_http_get),
        patch("app.services.jobs.sources.lever.httpx.get", side_effect=_http_get),
    ):
        service = ScheduledIngestionService(db, boards=boards)
        first = service.ingest_greenhouse_and_lever()
        second = service.ingest_greenhouse_and_lever()
    get_settings.cache_clear()

    assert first is not None
    assert first.fetched == 2
    assert first.inserted == 2
    assert first.current_fetch_datetime is not None
    assert first.last_fetch_datetime is None
    assert second is not None
    assert second.last_fetch_datetime == first.current_fetch_datetime
    assert db.query(Job).count() == 2
    sources = service.sources.list_active_boards()
    assert all(item.current_fetch_datetime is not None for item in sources)


def test_ingest_boards_api(
    client: TestClient, user_a: dict, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("JOB_INGEST_BOARD_DELAY_SECONDS", "0")
    get_settings.cache_clear()
    boards = [BoardRef("greenhouse", "acme", "Acme")]
    with (
        patch(
            "app.services.scheduled_ingestion_service.load_board_catalog",
            return_value=boards,
        ),
        patch("app.services.jobs.sources.greenhouse.httpx.get", return_value=_gh_response()),
    ):
        unauthorized = client.post("/api/v1/jobs/ingest/boards")
        assert unauthorized.status_code == 401
        response = client.post("/api/v1/jobs/ingest/boards", headers=auth_header(user_a))
    get_settings.cache_clear()
    assert response.status_code == 200
    body = response.json()
    assert body["fetched"] == 1
    assert body["inserted"] == 1
    assert body["current_fetch_datetime"]
    latest = client.get("/api/v1/jobs/fetch-runs/latest", headers=auth_header(user_a))
    assert latest.status_code == 200
    assert latest.json()["id"] == body["id"]
