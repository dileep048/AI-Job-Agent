from fastapi.testclient import TestClient
from tests.conftest import auth_header


def test_register(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "password123", "name": "New"},
    )
    assert response.status_code == 201
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert "password" not in body
    assert "password_hash" not in body


def test_duplicate_email(client: TestClient, user_a: dict) -> None:
    del user_a
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "a@example.com", "password": "password123"},
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "EMAIL_TAKEN"


def test_login(client: TestClient, user_a: dict) -> None:
    del user_a
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "a@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_password_hasher_uses_interactive_parameters() -> None:
    from argon2 import extract_parameters

    from app.security.password import hash_password

    params = extract_parameters(hash_password("password123"))
    assert params.memory_cost == 19456
    assert params.time_cost == 2
    assert params.parallelism == 1


def test_wrong_password(client: TestClient, user_a: dict) -> None:
    del user_a
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "a@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401
    assert "password" not in response.text.lower() or "Invalid email or password" in response.text


def test_me(client: TestClient, user_a: dict) -> None:
    response = client.get("/api/v1/auth/me", headers=auth_header(user_a))
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "a@example.com"
    assert "password_hash" not in body


def test_unauthenticated_access(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_refresh(client: TestClient, user_a: dict) -> None:
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": user_a["refresh_token"]})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
