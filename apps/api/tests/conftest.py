from __future__ import annotations

import io
import zipfile
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.config.settings import get_settings
from app.db import get_db
from app.main import app
from app.models import Base

get_settings.cache_clear()
settings = get_settings()

TEST_DATABASE_URL = settings.database_url.replace("/job_agent", "/job_agent_test")
if TEST_DATABASE_URL == settings.database_url:
    TEST_DATABASE_URL = settings.database_url + "_test"


def _ensure_test_database() -> None:
    admin_url = settings.database_url.rsplit("/", 1)[0] + "/postgres"
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    db_name = TEST_DATABASE_URL.rsplit("/", 1)[-1]
    with admin_engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": db_name},
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))
    admin_engine.dispose()


_ensure_test_database()

engine = create_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="session", autouse=True)
def _create_schema() -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(autouse=True)
def _reset_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[None, None, None]:
    monkeypatch.setenv("LOCAL_STORAGE_PATH", str(tmp_path))
    get_settings.cache_clear()
    with engine.begin() as conn:
        conn.execute(
            text(
                "TRUNCATE TABLE job_matches, job_fetch_runs, job_skills, jobs, job_sources, users RESTART IDENTITY CASCADE"
            )
        )
    yield
    get_settings.cache_clear()


@pytest.fixture
def db() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(_reset_db: None) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def user_a(client: TestClient) -> dict:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "a@example.com", "password": "password123", "name": "User A"},
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def user_b(client: TestClient) -> dict:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "b@example.com", "password": "password123", "name": "User B"},
    )
    assert response.status_code == 201
    return response.json()


def auth_header(token_payload: dict) -> dict[str, str]:
    return {"Authorization": f"Bearer {token_payload['access_token']}"}


def create_profile(client: TestClient, token: dict) -> dict:
    response = client.post(
        "/api/v1/profile",
        headers=auth_header(token),
        json={
            "headline": "Backend Engineer",
            "summary": "Builds APIs",
            "years_experience": 5,
            "current_role": "Senior Engineer",
            "current_company": "Acme",
            "preferred_locations": ["Bengaluru"],
            "preferred_job_types": ["full-time"],
            "minimum_salary": 2000000,
            "maximum_salary": 4000000,
            "salary_currency": "INR",
            "remote_preference": "hybrid",
        },
    )
    assert response.status_code == 201
    return response.json()


MIN_PDF = b"""%PDF-1.1
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 3 3]>>endobj
trailer<</Root 1 0 R>>
%%EOF
"""


def min_docx() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(
            "[Content_Types].xml",
            (
                '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org'
                '/package/2006/content-types"><Default Extension="xml" '
                'ContentType="application/xml"/></Types>'
            ),
        )
        archive.writestr(
            "word/document.xml",
            """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body><w:p><w:r><w:t>Resume</w:t></w:r></w:p></w:body>
</w:document>""",
        )
    return buffer.getvalue()
