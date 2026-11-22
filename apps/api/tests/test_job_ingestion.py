from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.conftest import auth_header

from app.models.job_source import JobSource
from app.repositories.job_repository import JobRepository, JobSearchFilters
from app.services.job_ingestion_service import JobIngestionService
from app.services.jobs.sources.manual import ManualJobSourceAdapter


def _ingest(db: Session) -> tuple[JobIngestionService, JobSource]:
    source = JobSource(name="Manual", source_type="manual", configuration={})
    db.add(source)
    db.commit()
    db.refresh(source)
    return JobIngestionService(db, adapter=ManualJobSourceAdapter()), source


def test_ingest_new_and_idempotent(db: Session) -> None:
    service, source = _ingest(db)
    jobs = [
        {
            "title": "Backend Engineer",
            "company_name": "Acme",
            "external_id": "1",
            "description": "Python APIs",
            "location": "Bengaluru",
        }
    ]
    first = service.ingest(source_id=source.id, configuration={"jobs": jobs})
    assert first.fetched == 1
    assert first.inserted == 1
    assert first.failed == 0
    db.refresh(source)
    first_current = source.current_fetch_datetime
    assert first_current is not None
    assert source.last_fetch_datetime is None
    second = service.ingest(source_id=source.id, configuration={"jobs": jobs})
    assert second.inserted == 0
    assert second.duplicates == 1
    db.refresh(source)
    assert source.last_fetch_datetime == first_current
    assert source.current_fetch_datetime is not None
    repo = JobRepository(db)
    items, total = repo.search(JobSearchFilters(), page=1, page_size=20)
    assert total == 1
    assert items[0].external_id == "1"


def test_same_source_external_id_updates(db: Session) -> None:
    service, source = _ingest(db)
    first = service.ingest(
        source_id=source.id,
        configuration={
            "jobs": [
                {
                    "title": "Backend Engineer",
                    "company_name": "Acme",
                    "external_id": "gh-1",
                    "description": "v1",
                }
            ]
        },
    )
    assert first.inserted == 1
    second = service.ingest(
        source_id=source.id,
        configuration={
            "jobs": [
                {
                    "title": "Backend Engineer",
                    "company_name": "Acme",
                    "external_id": "gh-1",
                    "description": "v2",
                }
            ]
        },
    )
    assert second.updated == 1
    items, total = JobRepository(db).search(JobSearchFilters(), page=1, page_size=10)
    assert total == 1
    assert items[0].description == "v2"


def test_content_hash_dedup(db: Session) -> None:
    service, source = _ingest(db)
    job = {
        "title": "Data Engineer",
        "company_name": "Globex",
        "location": "Remote",
        "description": "Pipelines",
    }
    service.ingest(source_id=source.id, configuration={"jobs": [{**job, "external_id": "a"}]})
    result = service.ingest(source_id=source.id, configuration={"jobs": [{**job, "external_id": "b"}]})
    assert result.inserted == 0
    _, total = JobRepository(db).search(JobSearchFilters(), page=1, page_size=10)
    assert total == 1


def test_mixed_success_and_failed(db: Session) -> None:
    service, source = _ingest(db)
    result = service.ingest(
        source_id=source.id,
        configuration={
            "jobs": [
                {"title": "Good", "company_name": "Acme"},
                {"title": "Missing company"},
                {"title": "Also good", "company_name": "Acme"},
            ]
        },
    )
    assert result.fetched == 3
    assert result.inserted == 2
    assert result.failed == 1
    assert result.errors


def test_ingest_api(client: TestClient, user_a: dict) -> None:
    response = client.post(
        "/api/v1/jobs/ingest",
        headers=auth_header(user_a),
        json={
            "source_type": "manual",
            "configuration": {
                "jobs": [
                    {
                        "title": "Staff Engineer",
                        "company_name": "Acme",
                        "description": "Lead teams",
                    }
                ]
            },
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "manual"
    assert body["fetched"] == 1
    assert body["inserted"] == 1


def test_import_unsupported_url(client: TestClient, user_a: dict) -> None:
    response = client.post(
        "/api/v1/jobs/from-url",
        headers=auth_header(user_a),
        json={"url": "https://linkedin.com/jobs/view/1"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "UNSUPPORTED_JOB_URL"


def test_import_greenhouse_job_url(client: TestClient, user_a: dict) -> None:
    payload = {
        "id": 6123695,
        "title": "Staff Engineer",
        "content": "Build products",
        "absolute_url": "https://boards.greenhouse.io/coinbase/jobs/6123695",
        "location": {"name": "Remote"},
    }
    response = Mock(status_code=200)
    response.json.return_value = payload
    with patch("app.services.jobs.sources.greenhouse.httpx.get", return_value=response):
        imported = client.post(
            "/api/v1/jobs/from-url",
            headers=auth_header(user_a),
            json={"url": "https://boards.greenhouse.io/coinbase/jobs/6123695"},
        )
    assert imported.status_code == 200
    body = imported.json()
    assert body["source"] == "greenhouse"
    assert body["inserted"] == 1
    listed = client.get("/api/v1/job-sources", headers=auth_header(user_a))
    assert any(item["external_key"] == "coinbase" for item in listed.json())
    sources = listed.json()
    coinbase = next(item for item in sources if item["external_key"] == "coinbase")
    assert "job_id" not in str(coinbase)


def test_add_source_without_fetch(client: TestClient, user_a: dict) -> None:
    response = client.post(
        "/api/v1/job-sources",
        headers=auth_header(user_a),
        json={
            "url": "https://boards.greenhouse.io/coinbase",
            "name": "Coinbase",
            "fetch_now": False,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["source_type"] == "greenhouse"
    assert body["external_key"] == "coinbase"
    assert body["ingest"] is None
    again = client.post(
        "/api/v1/job-sources",
        headers=auth_header(user_a),
        json={"source_type": "greenhouse", "token": "coinbase", "fetch_now": False},
    )
    assert again.json()["id"] == body["id"]


def test_repository_lookups(db: Session) -> None:
    service, source = _ingest(db)
    service.ingest(
        source_id=source.id,
        configuration={
            "jobs": [
                {
                    "title": "QA Engineer",
                    "company_name": "Acme",
                    "external_id": "qa-1",
                    "description": "Test",
                    "location": "Pune",
                }
            ]
        },
    )
    repo = JobRepository(db)
    found = repo.get_by_source_external(source.id, "qa-1")
    assert found is not None
    hashed = repo.get_by_content_hash(found.content_hash)
    assert hashed is not None
    hashed.title = "QA Engineer II"
    repo.save(hashed)
    repo.delete(hashed)
    assert repo.get_by_id(hashed.id) is None
