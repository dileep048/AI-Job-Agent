from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import parse_qs, unquote, urlparse

from app.exceptions import ValidationAppError

_GREENHOUSE_HOSTS = {"boards.greenhouse.io", "job-boards.greenhouse.io"}
_LEVER_HOSTS = {"jobs.lever.co"}
_SKIP_GREENHOUSE_HOSTS = {
    "boards-api.greenhouse.io",
    "www.greenhouse.io",
    "greenhouse.io",
    "support.greenhouse.io",
}


@dataclass(frozen=True)
class ParsedAtsUrl:
    source_type: str
    key: str
    job_id: str | None
    original_url: str

    @property
    def is_job(self) -> bool:
        return self.job_id is not None

    def ingest_configuration(self) -> dict[str, str]:
        if self.source_type == "greenhouse":
            config = {"board_token": self.key, "company_name": self.key}
            if self.job_id:
                config["job_id"] = self.job_id
            return config
        config = {"site": self.key, "company_name": self.key}
        if self.job_id:
            config["job_id"] = self.job_id
        return config

    def source_configuration(self) -> dict[str, str]:
        if self.source_type == "greenhouse":
            return {"board_token": self.key, "company_name": self.key}
        return {"site": self.key, "company_name": self.key}

    def base_url(self) -> str:
        if self.source_type == "greenhouse":
            return f"https://boards.greenhouse.io/{self.key}"
        return f"https://jobs.lever.co/{self.key}"


def parse_ats_url(url: str) -> ParsedAtsUrl | None:
    raw = (url or "").strip()
    if not raw:
        return None
    if "://" not in raw:
        raw = f"https://{raw}"
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"}:
        return None
    host = (parsed.hostname or "").lower()
    parts = [unquote(part) for part in parsed.path.split("/") if part]
    query = parse_qs(parsed.query)

    greenhouse = _parse_greenhouse(host, parts, query, raw)
    if greenhouse:
        return greenhouse
    return _parse_lever(host, parts, raw)


def require_ats_url(url: str) -> ParsedAtsUrl:
    parsed = parse_ats_url(url)
    if parsed is None:
        raise ValidationAppError(
            "UNSUPPORTED_JOB_URL",
            "Use a Greenhouse or Lever job or board URL. Other sites can be added as a manual job.",
        )
    return parsed


def _parse_greenhouse(
    host: str, parts: list[str], query: dict[str, list[str]], raw: str
) -> ParsedAtsUrl | None:
    token: str | None = None
    job_id: str | None = None

    if host in _GREENHOUSE_HOSTS:
        if not parts:
            return None
        token = parts[0]
        if len(parts) >= 3 and parts[1] in {"jobs", "job"}:
            job_id = parts[2]
    elif host.endswith(".greenhouse.io") and host not in _SKIP_GREENHOUSE_HOSTS:
        token = host.split(".", 1)[0]
        if len(parts) >= 2 and parts[0] in {"jobs", "job"}:
            job_id = parts[1]
        elif len(parts) >= 3 and parts[1] in {"jobs", "job"}:
            job_id = parts[2]
    else:
        return None

    if not token:
        return None
    board_for = (query.get("for") or [None])[0]
    if board_for:
        token = board_for
    gh_jid = (query.get("gh_jid") or query.get("token") or [None])[0]
    if gh_jid and not job_id:
        job_id = gh_jid
    return ParsedAtsUrl("greenhouse", token.strip().lower(), _clean_id(job_id), raw)


def _parse_lever(host: str, parts: list[str], raw: str) -> ParsedAtsUrl | None:
    if host not in _LEVER_HOSTS or not parts:
        return None
    site = parts[0].strip().lower()
    job_id = None
    if len(parts) >= 2 and parts[1].lower() not in {"apply"}:
        job_id = parts[1]
    return ParsedAtsUrl("lever", site, _clean_id(job_id), raw)


def _clean_id(value: str | None) -> str | None:
    if not value:
        return None
    text = value.strip()
    return text or None
