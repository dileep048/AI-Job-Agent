from fastapi.testclient import TestClient
from tests.conftest import auth_header, create_profile


def test_create_and_get_profile(client: TestClient, user_a: dict) -> None:
    created = create_profile(client, user_a)
    assert created["headline"] == "Backend Engineer"
    response = client.get("/api/v1/profile", headers=auth_header(user_a))
    assert response.status_code == 200
    assert response.json()["current_role"] == "Senior Engineer"


def test_update_profile(client: TestClient, user_a: dict) -> None:
    create_profile(client, user_a)
    response = client.put(
        "/api/v1/profile",
        headers=auth_header(user_a),
        json={
            "headline": "Staff Engineer",
            "summary": "Leads teams",
            "years_experience": 8,
            "current_role": "Staff Engineer",
            "current_company": "Acme",
            "preferred_locations": ["Remote"],
            "preferred_job_types": ["full-time"],
            "minimum_salary": 3000000,
            "maximum_salary": 5000000,
            "salary_currency": "INR",
            "remote_preference": "remote",
        },
    )
    assert response.status_code == 200
    assert response.json()["headline"] == "Staff Engineer"


def test_delete_profile(client: TestClient, user_a: dict) -> None:
    create_profile(client, user_a)
    response = client.delete("/api/v1/profile", headers=auth_header(user_a))
    assert response.status_code == 204
    response = client.get("/api/v1/profile", headers=auth_header(user_a))
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "PROFILE_NOT_FOUND"


def test_profile_user_isolation(client: TestClient, user_a: dict, user_b: dict) -> None:
    create_profile(client, user_a)
    response = client.get("/api/v1/profile", headers=auth_header(user_b))
    assert response.status_code == 404
