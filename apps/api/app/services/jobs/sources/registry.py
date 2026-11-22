from app.exceptions import ValidationAppError
from app.services.jobs.sources.base import JobSourceAdapter
from app.services.jobs.sources.greenhouse import GreenhouseJobSourceAdapter
from app.services.jobs.sources.lever import LeverJobSourceAdapter
from app.services.jobs.sources.manual import ManualJobSourceAdapter

_ADAPTERS: dict[str, type[JobSourceAdapter]] = {
    "manual": ManualJobSourceAdapter,
    "greenhouse": GreenhouseJobSourceAdapter,
    "lever": LeverJobSourceAdapter,
}


def get_adapter(source_type: str) -> JobSourceAdapter:
    cls = _ADAPTERS.get(source_type.lower())
    if cls is None:
        raise ValidationAppError(
            "UNSUPPORTED_SOURCE",
            f"Unsupported job source type: {source_type}",
        )
    return cls()
