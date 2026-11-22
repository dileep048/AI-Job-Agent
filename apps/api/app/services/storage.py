from abc import ABC, abstractmethod
from pathlib import Path
from uuid import UUID, uuid4

from app.config import get_settings
from app.exceptions import NotFoundError


class StorageService(ABC):
    @abstractmethod
    def upload(self, data: bytes, *, content_type: str, extension: str, user_id: UUID) -> str:
        """Store bytes and return an opaque storage key."""

    @abstractmethod
    def download(self, key: str) -> bytes:
        """Return file bytes for a storage key."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete an object if it exists."""

    @abstractmethod
    def get_url(self, key: str) -> str:
        """Return a locator for the object (path or signed URL later)."""


class LocalStorageService(StorageService):
    def __init__(self, root: str | None = None) -> None:
        settings = get_settings()
        self.root = Path(root or settings.local_storage_path).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def upload(self, data: bytes, *, content_type: str, extension: str, user_id: UUID) -> str:
        del content_type
        safe_ext = extension.lower().lstrip(".")
        key = f"resumes/{user_id}/{uuid4().hex}.{safe_ext}"
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return key

    def download(self, key: str) -> bytes:
        path = self._resolve(key)
        if not path.exists() or not path.is_file():
            raise NotFoundError("FILE_NOT_FOUND", "File not found")
        return path.read_bytes()

    def delete(self, key: str) -> None:
        path = self._resolve(key)
        if path.exists() and path.is_file():
            path.unlink()

    def get_url(self, key: str) -> str:
        return key

    def _resolve(self, key: str) -> Path:
        if ".." in Path(key).parts or key.startswith("/"):
            raise NotFoundError("FILE_NOT_FOUND", "File not found")
        path = (self.root / key).resolve()
        if not str(path).startswith(str(self.root)):
            raise NotFoundError("FILE_NOT_FOUND", "File not found")
        return path


def get_storage_service() -> StorageService:
    settings = get_settings()
    backend = settings.storage_backend.lower()
    if backend == "local":
        return LocalStorageService()
    raise RuntimeError(f"Unsupported storage backend: {backend}")
