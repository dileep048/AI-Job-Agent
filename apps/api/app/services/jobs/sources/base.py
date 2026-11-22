from abc import ABC, abstractmethod
from typing import Any


class JobSourceAdapter(ABC):
    source_type: str

    @abstractmethod
    def fetch_jobs(self, configuration: dict[str, Any]) -> list[dict[str, Any]]:
        """Return source-native job payloads (not yet normalized)."""
