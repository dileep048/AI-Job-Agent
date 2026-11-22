from typing import Any

import httpx

from app.exceptions import ValidationAppError
from app.services.jobs.sources.base import JobSourceAdapter

GREENHOUSE_URL = "https://boards-api.greenhouse.io/v1/boards/{token}/jobs"


class GreenhouseJobSourceAdapter(JobSourceAdapter):
    source_type = "greenhouse"

    def fetch_jobs(self, configuration: dict[str, Any]) -> list[dict[str, Any]]:
        token = str(configuration.get("board_token") or configuration.get("token") or "").strip()
        if not token:
            raise ValidationAppError("INVALID_SOURCE_CONFIG", "Greenhouse board_token is required")
        job_id = str(configuration.get("job_id") or "").strip()
        company_name = configuration.get("company_name") or token
        if job_id:
            raw = self._get_json(f"{GREENHOUSE_URL.format(token=token)}/{job_id}", configuration)
            if not isinstance(raw, dict) or raw.get("id") is None:
                return []
            mapped = _map_job(raw, token, company_name)
            return [mapped] if mapped else []

        payload = self._get_json(
            GREENHOUSE_URL.format(token=token),
            configuration,
            params={"content": "true"},
        )
        jobs = payload.get("jobs") if isinstance(payload, dict) else payload
        if not isinstance(jobs, list):
            return []
        mapped_jobs: list[dict[str, Any]] = []
        for raw in jobs:
            mapped = _map_job(raw, token, company_name)
            if mapped:
                mapped_jobs.append(mapped)
        return mapped_jobs

    def _get_json(
        self,
        url: str,
        configuration: dict[str, Any],
        params: dict[str, str] | None = None,
    ) -> Any:
        response = httpx.get(url, params=params or {"content": "true"}, timeout=30.0)
        if response.status_code >= 400:
            if configuration.get("skip_http_errors"):
                return {}
            raise ValidationAppError(
                "SOURCE_FETCH_FAILED",
                "Could not fetch jobs from Greenhouse",
            )
        return response.json()


def _map_job(raw: Any, token: str, company_name: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    location = None
    loc = raw.get("location")
    if isinstance(loc, dict):
        location = loc.get("name")
    departments = raw.get("departments") or []
    department = None
    if departments and isinstance(departments[0], dict):
        department = departments[0].get("name")
    offices = raw.get("offices") or []
    locations = []
    for office in offices:
        if isinstance(office, dict) and office.get("name"):
            locations.append(office["name"])
    return {
        "external_id": str(raw.get("id")) if raw.get("id") is not None else None,
        "title": raw.get("title") or raw.get("text"),
        "company_name": company_name or raw.get("company_name") or token,
        "source_url": raw.get("absolute_url"),
        "description": raw.get("content"),
        "location": location,
        "locations": locations or ([location] if location else []),
        "department": department,
        "posted_at": raw.get("updated_at") or raw.get("created_at"),
        "raw_data": raw,
    }
