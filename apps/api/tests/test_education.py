from fastapi.testclient import TestClient
from tests.conftest import auth_header, create_profile


def test_education_crud(client: TestClient, user_a: dict) -> None:
    create_profile(client, user_a)
    created = client.post(
        "/api/v1/profile/education",
        headers=auth_header(user_a),
        json={
            "institution": "IIT",
            "degree": "B.Tech",
            "field_of_study": "Computer Science",
            "start_date": "2012-08-01",
            "end_date": "2016-05-01",
        },
    )
    assert created.status_code == 201
    edu_id = created.json()["id"]
    updated = client.put(
        f"/api/v1/profile/education/{edu_id}",
        headers=auth_header(user_a),
        json={"degree": "B.Tech Hons"},
    )
    assert updated.status_code == 200
    deleted = client.delete(f"/api/v1/profile/education/{edu_id}", headers=auth_header(user_a))
    assert deleted.status_code == 204


def test_education_user_isolation(client: TestClient, user_a: dict, user_b: dict) -> None:
    create_profile(client, user_a)
    create_profile(client, user_b)
    created = client.post(
        "/api/v1/profile/education",
        headers=auth_header(user_a),
        json={"institution": "IIT"},
    )
    response = client.get("/api/v1/profile/education", headers=auth_header(user_b))
    assert response.json() == []
    response = client.delete(
        f"/api/v1/profile/education/{created.json()['id']}",
        headers=auth_header(user_b),
    )
    assert response.status_code == 404
