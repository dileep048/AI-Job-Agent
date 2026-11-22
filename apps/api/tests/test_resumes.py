from fastapi.testclient import TestClient
from tests.conftest import MIN_PDF, auth_header, min_docx


def test_upload_pdf(client: TestClient, user_a: dict) -> None:
    response = client.post(
        "/api/v1/resumes/upload",
        headers=auth_header(user_a),
        files={"file": ("resume.pdf", MIN_PDF, "application/pdf")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["file_name"] == "resume.pdf"
    assert body["status"] == "uploaded"
    assert body["is_default"] is True
    assert "resume_data" in body


def test_upload_docx(client: TestClient, user_a: dict) -> None:
    response = client.post(
        "/api/v1/resumes/upload",
        headers=auth_header(user_a),
        files={
            "file": (
                "resume.docx",
                min_docx(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert response.status_code == 201
    assert response.json()["file_name"] == "resume.docx"


def test_reject_invalid_type(client: TestClient, user_a: dict) -> None:
    response = client.post(
        "/api/v1/resumes/upload",
        headers=auth_header(user_a),
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_FILE_TYPE"


def test_reject_oversize(client: TestClient, user_a: dict) -> None:
    huge = b"%PDF-" + b"a" * (10 * 1024 * 1024 + 1)
    response = client.post(
        "/api/v1/resumes/upload",
        headers=auth_header(user_a),
        files={"file": ("resume.pdf", huge, "application/pdf")},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "FILE_TOO_LARGE"


def test_list_delete_set_default(client: TestClient, user_a: dict) -> None:
    first = client.post(
        "/api/v1/resumes/upload",
        headers=auth_header(user_a),
        files={"file": ("one.pdf", MIN_PDF, "application/pdf")},
    ).json()
    second = client.post(
        "/api/v1/resumes/upload",
        headers=auth_header(user_a),
        files={"file": ("two.pdf", MIN_PDF, "application/pdf")},
    ).json()
    listed = client.get("/api/v1/resumes", headers=auth_header(user_a))
    assert listed.status_code == 200
    assert len(listed.json()) == 2
    updated = client.post(
        f"/api/v1/resumes/{second['id']}/set-default",
        headers=auth_header(user_a),
    )
    assert updated.status_code == 200
    assert updated.json()["is_default"] is True
    first_after = client.get(f"/api/v1/resumes/{first['id']}", headers=auth_header(user_a))
    assert first_after.json()["is_default"] is False
    deleted = client.delete(f"/api/v1/resumes/{second['id']}", headers=auth_header(user_a))
    assert deleted.status_code == 204


def test_resume_user_isolation(client: TestClient, user_a: dict, user_b: dict) -> None:
    created = client.post(
        "/api/v1/resumes/upload",
        headers=auth_header(user_a),
        files={"file": ("resume.pdf", MIN_PDF, "application/pdf")},
    ).json()
    response = client.get(f"/api/v1/resumes/{created['id']}", headers=auth_header(user_b))
    assert response.status_code == 404
    download = client.get(f"/api/v1/resumes/{created['id']}/download", headers=auth_header(user_b))
    assert download.status_code == 404
    listed = client.get("/api/v1/resumes", headers=auth_header(user_b))
    assert listed.json() == []
