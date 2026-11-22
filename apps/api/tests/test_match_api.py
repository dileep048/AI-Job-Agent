from fastapi.testclient import TestClient
from tests.conftest import auth_header, create_profile


def test_match_requires_profile(client: TestClient, user_a: dict) -> None:
    job = client.post(
        "/api/v1/jobs",
        headers=auth_header(user_a),
        json={"title": "Engineer", "company_name": "Acme", "description": "Python"},
    ).json()
    response = client.post(f"/api/v1/jobs/{job['id']}/match", headers=auth_header(user_a))
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "PROFILE_REQUIRED"


def test_score_job_and_isolate_users(client: TestClient, user_a: dict, user_b: dict) -> None:
    create_profile(client, user_a)
    client.post(
        "/api/v1/profile/skills",
        headers=auth_header(user_a),
        json={"skill_name": "Python"},
    )
    job = client.post(
        "/api/v1/jobs",
        headers=auth_header(user_a),
        json={
            "title": "Python Engineer",
            "company_name": "Acme",
            "description": "5+ years of experience with Python and FastAPI in Bengaluru.",
            "location": "Bengaluru",
            "workplace_type": "hybrid",
            "employment_type": "full_time",
            "skills": ["Python", "FastAPI"],
            "salary_min": 2500000,
            "salary_max": 3500000,
            "salary_currency": "INR",
        },
    ).json()
    scored = client.post(f"/api/v1/jobs/{job['id']}/match", headers=auth_header(user_a))
    assert scored.status_code == 200
    body = scored.json()
    assert body["job_id"] == job["id"]
    assert 0 <= body["overall_score"] <= 100
    assert body["recommendation"] in {"APPLY", "CONSIDER", "SKIP"}
    assert body["explanation_source"] == "rules"
    assert "Python" in body["matched_skills"]
    fetched = client.get(f"/api/v1/jobs/{job['id']}/match", headers=auth_header(user_a))
    assert fetched.status_code == 200
    other = client.get(f"/api/v1/jobs/{job['id']}/match", headers=auth_header(user_b))
    assert other.status_code == 404
    listed = client.get("/api/v1/matches", headers=auth_header(user_a))
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    jobs = client.get("/api/v1/jobs", headers=auth_header(user_a))
    assert jobs.json()["items"][0]["match_score"] == body["overall_score"]
    hidden = client.get("/api/v1/jobs", headers=auth_header(user_b))
    assert hidden.json()["items"][0].get("match_score") is None
