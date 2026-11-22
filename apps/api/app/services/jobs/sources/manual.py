from typing import Any

from app.services.jobs.sources.base import JobSourceAdapter


class ManualJobSourceAdapter(JobSourceAdapter):
    source_type = "manual"

    def fetch_jobs(self, configuration: dict[str, Any]) -> list[dict[str, Any]]:
        jobs = configuration.get("jobs") or []
        if not isinstance(jobs, list):
            return []
        return [job for job in jobs if isinstance(job, dict)]
