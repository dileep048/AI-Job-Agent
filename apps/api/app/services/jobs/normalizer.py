import hashlib
import html
import re
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from app.exceptions import ValidationAppError
from app.services.jobs.dto import NormalizedJob

_WS = re.compile(r"\s+")
_BREAK = re.compile(r"(?i)<br\s*/?>")
_BLOCK_END = re.compile(r"(?i)</(p|div|h[1-6]|li|tr|section|article)>")
_TAG = re.compile(r"<[^>]+>")


def html_to_plain_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    for _ in range(3):
        decoded = html.unescape(text)
        if decoded == text:
            break
        text = decoded
    text = text.replace("\xa0", " ")
    text = _BREAK.sub("\n", text)
    text = _BLOCK_END.sub("\n", text)
    text = _TAG.sub("", text)
    text = html.unescape(text).replace("\xa0", " ")
    lines = [_WS.sub(" ", line).strip() for line in text.splitlines()]
    text = "\n".join(line for line in lines if line)
    return text or None

EMPLOYMENT_MAP = {
    "full_time": "full_time",
    "full-time": "full_time",
    "fulltime": "full_time",
    "full time": "full_time",
    "part_time": "part_time",
    "part-time": "part_time",
    "parttime": "part_time",
    "part time": "part_time",
    "contract": "contract",
    "contractor": "contract",
    "internship": "internship",
    "intern": "internship",
    "temporary": "temporary",
    "temp": "temporary",
    "freelance": "contract",
}

WORKPLACE_MAP = {
    "remote": "remote",
    "work from home": "remote",
    "wfh": "remote",
    "hybrid": "hybrid",
    "onsite": "onsite",
    "on-site": "onsite",
    "on site": "onsite",
    "office": "onsite",
    "in office": "onsite",
}


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = _WS.sub(" ", str(value)).strip()
    return text or None


def normalize_employment_type(value: Any) -> str | None:
    text = clean_text(value)
    if text is None:
        return None
    return EMPLOYMENT_MAP.get(text.lower(), "other")


def normalize_workplace_type(value: Any) -> str | None:
    text = clean_text(value)
    if text is None:
        return None
    key = text.lower()
    for needle, mapped in WORKPLACE_MAP.items():
        if needle in key:
            return mapped
    return "unknown"


def normalize_locations(value: Any) -> list[str]:
    items: list[str] = []
    if value is None:
        return items
    if isinstance(value, str):
        parts = [value]
    elif isinstance(value, list):
        parts = value
    else:
        parts = [str(value)]
    seen: set[str] = set()
    for part in parts:
        cleaned = clean_text(part)
        if cleaned is None:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        items.append(cleaned)
    return items


def _decimal(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    if parsed < 0:
        return None
    return parsed


def _datetime(value: Any) -> datetime | None:
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, int | float):
        ts = float(value)
        if ts > 10_000_000_000:
            ts = ts / 1000
        return datetime.fromtimestamp(ts, tz=UTC)
    text = clean_text(value)
    if text is None:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def content_hash(
    *, company_name: str, title: str, location: str | None, description: str | None
) -> str:
    payload = "|".join(
        [
            (company_name or "").strip().lower(),
            (title or "").strip().lower(),
            (location or "").strip().lower(),
            (description or "").strip().lower(),
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class JobNormalizationService:
    def normalize(self, payload: dict[str, Any]) -> NormalizedJob:
        title = clean_text(payload.get("title"))
        company_name = clean_text(payload.get("company_name") or payload.get("company"))
        if not title or not company_name:
            raise ValidationAppError("INVALID_JOB", "Job title and company_name are required")

        locations = normalize_locations(payload.get("locations") or payload.get("location"))
        location = clean_text(payload.get("location")) or (locations[0] if locations else None)
        if location and location not in locations:
            locations = [location, *locations]

        description = html_to_plain_text(payload.get("description"))

        job = NormalizedJob(
            external_id=clean_text(payload.get("external_id")),
            source_url=clean_text(payload.get("source_url")),
            title=title,
            company_name=company_name,
            company_url=clean_text(payload.get("company_url")),
            description=description,
            location=location,
            locations=locations,
            employment_type=normalize_employment_type(payload.get("employment_type")),
            workplace_type=normalize_workplace_type(payload.get("workplace_type")),
            salary_min=_decimal(payload.get("salary_min")),
            salary_max=_decimal(payload.get("salary_max")),
            salary_currency=clean_text(payload.get("salary_currency")),
            department=clean_text(payload.get("department")),
            experience_level=clean_text(payload.get("experience_level")),
            posted_at=_datetime(payload.get("posted_at")),
            expires_at=_datetime(payload.get("expires_at")),
            is_active=bool(payload.get("is_active", True)),
            skills=[s for s in (clean_text(item) for item in payload.get("skills") or []) if s],
            raw_data=(
                payload.get("raw_data")
                if isinstance(payload.get("raw_data"), dict)
                else dict(payload)
            ),
        )
        return job

    def hash_for(self, job: NormalizedJob) -> str:
        return content_hash(
            company_name=job.company_name,
            title=job.title,
            location=job.location,
            description=job.description,
        )
