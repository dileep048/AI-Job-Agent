from fastapi.testclient import TestClient
from tests.conftest import auth_header, create_profile


def _create_skill(client: TestClient, token: dict, name: str = "Python") -> dict:
    response = client.post(
        "/api/v1/profile/skills",
        headers=auth_header(token),
        json={
            "skill_name": name,
            "skill_type": "Backend",
            "years_experience": 5,
            "proficiency": "Expert",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_update_delete_skill(client: TestClient, user_a: dict) -> None:
    create_profile(client, user_a)
    skill = _create_skill(client, user_a)
    skill_id = skill["id"]
    response = client.put(
        f"/api/v1/profile/skills/{skill_id}",
        headers=auth_header(user_a),
        json={"proficiency": "Advanced", "years_experience": 6},
    )
    assert response.status_code == 200
    assert response.json()["proficiency"] == "Advanced"
    response = client.delete(f"/api/v1/profile/skills/{skill_id}", headers=auth_header(user_a))
    assert response.status_code == 204
    listed = client.get("/api/v1/profile/skills", headers=auth_header(user_a))
    assert listed.json() == []


def test_duplicate_skill(client: TestClient, user_a: dict) -> None:
    create_profile(client, user_a)
    _create_skill(client, user_a)
    response = client.post(
        "/api/v1/profile/skills",
        headers=auth_header(user_a),
        json={"skill_name": "Python", "skill_type": "Backend"},
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "SKILL_EXISTS"


def test_skill_user_isolation(client: TestClient, user_a: dict, user_b: dict) -> None:
    create_profile(client, user_a)
    create_profile(client, user_b)
    skill = _create_skill(client, user_a)
    response = client.put(
        f"/api/v1/profile/skills/{skill['id']}",
        headers=auth_header(user_b),
        json={"proficiency": "Beginner"},
    )
    assert response.status_code == 404
    listed = client.get("/api/v1/profile/skills", headers=auth_header(user_b))
    assert listed.json() == []
