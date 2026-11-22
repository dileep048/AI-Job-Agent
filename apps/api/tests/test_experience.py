from fastapi.testclient import TestClient
from tests.conftest import auth_header, create_profile


def _create_experience(client: TestClient, token: dict, current: bool = False) -> dict:
    payload = {
        "company_name": "Acme",
        "job_title": "Engineer",
        "start_date": "2020-01-01",
        "end_date": None if current else "2023-01-01",
        "description": "Built APIs",
        "achievements": ["Shipped invoicing"],
        "technologies": ["Python", "FastAPI"],
    }
    response = client.post(
        "/api/v1/profile/experience",
        headers=auth_header(token),
        json=payload,
    )
    assert response.status_code == 201
    return response.json()


def test_create_update_delete_experience(client: TestClient, user_a: dict) -> None:
    create_profile(client, user_a)
    item = _create_experience(client, user_a)
    response = client.put(
        f"/api/v1/profile/experience/{item['id']}",
        headers=auth_header(user_a),
        json={"job_title": "Senior Engineer"},
    )
    assert response.status_code == 200
    assert response.json()["job_title"] == "Senior Engineer"
    response = client.delete(
        f"/api/v1/profile/experience/{item['id']}", headers=auth_header(user_a)
    )
    assert response.status_code == 204


def test_current_job(client: TestClient, user_a: dict) -> None:
    create_profile(client, user_a)
    item = _create_experience(client, user_a, current=True)
    assert item["end_date"] is None
    response = client.put(
        f"/api/v1/profile/experience/{item['id']}",
        headers=auth_header(user_a),
        json={"currently_working": True, "end_date": "2024-01-01"},
    )
    assert response.status_code == 200
    assert response.json()["end_date"] is None


def test_experience_user_isolation(client: TestClient, user_a: dict, user_b: dict) -> None:
    create_profile(client, user_a)
    create_profile(client, user_b)
    item = _create_experience(client, user_a)
    response = client.delete(
        f"/api/v1/profile/experience/{item['id']}", headers=auth_header(user_b)
    )
    assert response.status_code == 404
