import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from tests.conftest import auth_header

from app.models.job import Job
from app.models.job_skill import JobSkill
from app.models.job_source import JobSource


def _job_payload(**overrides: object) -> dict:
    payload = {
        "title": "Senior Backend Engineer",
        "company_name": "Acme",
        "description": "Build APIs in Python",
        "location": "Bengaluru",
        "employment_type": "full-time",
        "workplace_type": "Hybrid",
        "skills": ["Python", "FastAPI"],
    }
    payload.update(overrides)
    return payload


def test_create_job_requires_auth(client: TestClient) -> None:
    response = client.post("/api/v1/jobs", json=_job_payload())
    assert response.status_code == 401


def test_ingest_requires_auth(client: TestClient) -> None:
    response = client.post("/api/v1/jobs/ingest", json={"source_type": "manual", "configuration": {"jobs": []}})
    assert response.status_code == 401


def test_create_and_get_job(client: TestClient, user_a: dict) -> None:
    created = client.post("/api/v1/jobs", headers=auth_header(user_a), json=_job_payload())
    assert created.status_code == 201
    body = created.json()
    assert body["title"] == "Senior Backend Engineer"
    assert body["employment_type"] == "full_time"
    assert body["workplace_type"] == "hybrid"
    assert "raw_data" not in body
    job_id = body["id"]
    fetched = client.get(f"/api/v1/jobs/{job_id}", headers=auth_header(user_a))
    assert fetched.status_code == 200
    assert fetched.json()["company_name"] == "Acme"
    assert len(fetched.json()["skills"]) == 2


def test_list_search_filters_pagination(client: TestClient, user_a: dict) -> None:
    client.post("/api/v1/jobs", headers=auth_header(user_a), json=_job_payload())
    client.post(
        "/api/v1/jobs",
        headers=auth_header(user_a),
        json=_job_payload(title="Frontend Engineer", location="Remote", workplace_type="remote"),
    )
    listed = client.get("/api/v1/jobs?q=python&page=1&page_size=10", headers=auth_header(user_a))
    assert listed.status_code == 200
    data = listed.json()
    assert data["total"] >= 1
    assert "total_pages" in data
    assert data["page_size"] == 10
    remote = client.get("/api/v1/jobs?workplace_type=remote", headers=auth_header(user_a))
    assert remote.status_code == 200
    assert all(
        item["workplace_type"] == "remote" or (item["location"] or "").lower().find("remote") >= 0
        for item in remote.json()["items"]
    )
    office = client.get("/api/v1/jobs?location=Bengaluru", headers=auth_header(user_a))
    assert office.status_code == 200
    assert office.json()["total"] >= 1
    assert any("Bengaluru" in (item["location"] or "") for item in office.json()["items"])
    search = client.get("/api/v1/jobs?q=Frontend", headers=auth_header(user_a))
    assert search.json()["total"] >= 1
    assert all("Frontend" in item["title"] for item in search.json()["items"])


def test_update_and_delete_job(client: TestClient, user_a: dict) -> None:
    created = client.post("/api/v1/jobs", headers=auth_header(user_a), json=_job_payload()).json()
    updated = client.patch(
        f"/api/v1/jobs/{created['id']}",
        headers=auth_header(user_a),
        json={"description": "Updated description", "is_active": False},
    )
    assert updated.status_code == 200
    assert updated.json()["description"] == "Updated description"
    deleted = client.delete(f"/api/v1/jobs/{created['id']}", headers=auth_header(user_a))
    assert deleted.status_code == 204
    missing = client.get(f"/api/v1/jobs/{created['id']}", headers=auth_header(user_a))
    assert missing.status_code == 404


def test_invalid_job_id(client: TestClient, user_a: dict) -> None:
    response = client.get("/api/v1/jobs/not-a-uuid", headers=auth_header(user_a))
    assert response.status_code == 422


def test_missing_job_returns_404(client: TestClient, user_a: dict) -> None:
    response = client.get(
        "/api/v1/jobs/00000000-0000-0000-0000-000000000000",
        headers=auth_header(user_a),
    )
    assert response.status_code == 404


def test_jobs_are_global_not_user_owned(client: TestClient, user_a: dict, user_b: dict) -> None:
    created = client.post("/api/v1/jobs", headers=auth_header(user_a), json=_job_payload()).json()
    listed = client.get("/api/v1/jobs", headers=auth_header(user_b))
    assert any(item["id"] == created["id"] for item in listed.json()["items"])
    profile = client.get("/api/v1/profile", headers=auth_header(user_b))
    assert profile.status_code == 404


def test_job_model_constraints(db: Session) -> None:
    source = JobSource(name="Manual", source_type="manual", configuration={})
    db.add(source)
    db.commit()
    db.refresh(source)
    job = Job(
        source_id=source.id,
        external_id="ext-1",
        title="Engineer",
        company_name="Acme",
        content_hash="abc",
        raw_data={},
        locations=[],
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    db.add(JobSkill(job_id=job.id, skill_name="Python"))
    db.commit()
    skills = db.query(JobSkill).filter(JobSkill.job_id == job.id).all()
    assert len(skills) == 1
    db.add(JobSkill(job_id=job.id, skill_name="Python"))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()
