from typing import Any

import httpx

from app.exceptions import ValidationAppError
from app.services.jobs.sources.base import JobSourceAdapter

LEVER_URL = "https://api.lever.co/v0/postings/{site}"


class LeverJobSourceAdapter(JobSourceAdapter):
    source_type = "lever"

    def fetch_jobs(self, configuration: dict[str, Any]) -> list[dict[str, Any]]:
        site = str(configuration.get("site") or configuration.get("token") or "").strip()
        if not site:
            raise ValidationAppError("INVALID_SOURCE_CONFIG", "Lever site is required")
        job_id = str(configuration.get("job_id") or "").strip()
        company_name = configuration.get("company_name") or site
        if job_id:
            raw = self._get_json(f"{LEVER_URL.format(site=site)}/{job_id}", configuration)
            mapped = _map_job(raw, site, company_name)
            return [mapped] if mapped else []

        payload = self._get_json(
            LEVER_URL.format(site=site),
            configuration,
            params={"mode": "json"},
        )
        if not isinstance(payload, list):
            return []
        mapped_jobs: list[dict[str, Any]] = []
        for raw in payload:
            mapped = _map_job(raw, site, company_name)
            if mapped:
                mapped_jobs.append(mapped)
        return mapped_jobs

    def _get_json(
        self,
        url: str,
        configuration: dict[str, Any],
        params: dict[str, str] | None = None,
    ) -> Any:
        response = httpx.get(url, params=params or {"mode": "json"}, timeout=30.0)
        if response.status_code >= 400:
            if configuration.get("skip_http_errors"):
                return []
            raise ValidationAppError(
                "SOURCE_FETCH_FAILED",
                "Could not fetch jobs from Lever",
            )
        return response.json()


def _map_job(raw: Any, site: str, company_name: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    categories = raw.get("categories") if isinstance(raw.get("categories"), dict) else {}
    location = categories.get("location") if isinstance(categories, dict) else None
    return {
        "external_id": str(raw.get("id")) if raw.get("id") is not None else None,
        "title": raw.get("text"),
        "company_name": company_name or site,
        "source_url": raw.get("hostedUrl") or raw.get("applyUrl"),
        "description": raw.get("descriptionPlain") or raw.get("description"),
        "location": location,
        "locations": [location] if location else [],
        "employment_type": (categories.get("commitment") if isinstance(categories, dict) else None),
        "department": (
            (categories.get("team") or categories.get("department"))
            if isinstance(categories, dict)
            else None
        ),
        "workplace_type": raw.get("workplaceType"),
        "posted_at": raw.get("createdAt"),
        "raw_data": raw,
    }
