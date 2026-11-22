from uuid import UUID

from sqlalchemy.orm import Session

from app.config import get_settings
from app.exceptions import NotFoundError, ValidationAppError
from app.models.resume import DEFAULT_RESUME_DATA, Resume
from app.repositories.resume_repository import ResumeRepository
from app.schemas.resume import ResumeCreate, ResumeUpdate
from app.services.storage import StorageService, get_storage_service

ALLOWED_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
}
ALLOWED_EXTENSIONS = {"pdf", "docx"}
PDF_MAGIC = b"%PDF-"
ZIP_MAGIC = b"PK"


def _extension(filename: str | None) -> str:
    if not filename or "." not in filename:
        return ""
    return filename.rsplit(".", 1)[-1].lower()


def validate_upload(filename: str | None, content_type: str | None, data: bytes) -> str:
    settings = get_settings()
    if len(data) > settings.max_upload_bytes:
        raise ValidationAppError("FILE_TOO_LARGE", "File exceeds the 10 MB limit")
    if not data:
        raise ValidationAppError("FILE_EMPTY", "Uploaded file is empty")

    ext = _extension(filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationAppError("INVALID_FILE_TYPE", "Only PDF and DOCX files are allowed")

    mime = (content_type or "").split(";")[0].strip().lower()
    expected_ext = ALLOWED_TYPES.get(mime)
    if expected_ext is None or expected_ext != ext:
        raise ValidationAppError("INVALID_FILE_TYPE", "Only PDF and DOCX files are allowed")

    if ext == "pdf" and not data.startswith(PDF_MAGIC):
        raise ValidationAppError("INVALID_FILE_TYPE", "File content does not match a PDF")
    if ext == "docx" and not data.startswith(ZIP_MAGIC):
        raise ValidationAppError("INVALID_FILE_TYPE", "File content does not match a DOCX")
    return ext


class ResumeService:
    def __init__(self, db: Session, storage: StorageService | None = None) -> None:
        self.resumes = ResumeRepository(db)
        self.storage = storage or get_storage_service()

    def list(self, user_id: UUID) -> list[Resume]:
        return self.resumes.list_by_user(user_id)

    def get(self, user_id: UUID, resume_id: UUID) -> Resume:
        resume = self.resumes.get_by_id_and_user(resume_id, user_id)
        if resume is None:
            raise NotFoundError("RESUME_NOT_FOUND", "Resume not found")
        return resume

    def create(self, user_id: UUID, payload: ResumeCreate) -> Resume:
        resume = Resume(
            user_id=user_id,
            name=payload.name,
            resume_data=payload.resume_data.model_dump(),
            is_default=False,
            status="uploaded",
            version=1,
        )
        resume = self.resumes.create(resume)
        if payload.is_default or self.resumes.count_by_user(user_id) == 1:
            self.set_default(user_id, resume.id)
            return self.get(user_id, resume.id)
        return resume

    def update(self, user_id: UUID, resume_id: UUID, payload: ResumeUpdate) -> Resume:
        resume = self.get(user_id, resume_id)
        data = payload.model_dump(exclude_unset=True)
        is_default = data.pop("is_default", None)
        resume_data = data.pop("resume_data", None)
        for field, value in data.items():
            setattr(resume, field, value)
        if resume_data is not None:
            resume.resume_data = resume_data
            resume.version = (resume.version or 1) + 1
        resume = self.resumes.save(resume)
        if is_default:
            return self.set_default(user_id, resume.id)
        return resume

    def delete(self, user_id: UUID, resume_id: UUID) -> None:
        resume = self.get(user_id, resume_id)
        if resume.storage_key:
            self.storage.delete(resume.storage_key)
        was_default = resume.is_default
        self.resumes.delete(resume)
        if was_default:
            remaining = self.resumes.list_by_user(user_id)
            if remaining:
                self.set_default(user_id, remaining[0].id)

    def set_default(self, user_id: UUID, resume_id: UUID) -> Resume:
        resume = self.get(user_id, resume_id)
        self.resumes.clear_defaults(user_id, except_id=resume.id)
        resume.is_default = True
        return self.resumes.save(resume)

    def upload(
        self,
        user_id: UUID,
        *,
        filename: str | None,
        content_type: str | None,
        data: bytes,
    ) -> Resume:
        ext = validate_upload(filename, content_type, data)
        key = self.storage.upload(
            data,
            content_type=content_type or "",
            extension=ext,
            user_id=user_id,
        )
        original_name = (filename or f"resume.{ext}")[:255]
        resume = Resume(
            user_id=user_id,
            name=original_name.rsplit(".", 1)[0][:255] or "Resume",
            version=1,
            resume_data=DEFAULT_RESUME_DATA.copy(),
            file_url=self.storage.get_url(key),
            file_name=original_name,
            file_type=content_type,
            file_size=len(data),
            is_default=False,
            status="uploaded",
            storage_key=key,
        )
        resume = self.resumes.create(resume)
        if self.resumes.count_by_user(user_id) == 1:
            return self.set_default(user_id, resume.id)
        return resume

    def download(self, user_id: UUID, resume_id: UUID) -> tuple[Resume, bytes]:
        resume = self.get(user_id, resume_id)
        if not resume.storage_key:
            raise NotFoundError("FILE_NOT_FOUND", "No file is attached to this resume")
        return resume, self.storage.download(resume.storage_key)
