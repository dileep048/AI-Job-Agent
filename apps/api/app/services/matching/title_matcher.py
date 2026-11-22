from __future__ import annotations

import re

from app.services.matching.dto import CandidateEvidence, JobRequirements

_TOKEN = re.compile(r"[a-z0-9]+")


def match_title(candidate: CandidateEvidence, requirements: JobRequirements) -> float:
    job_title = (requirements.title or "").lower()
    if not job_title:
        return 50.0
    titles = [candidate.current_title or ""]
    titles.extend(item.get("job_title", "") for item in candidate.experiences)
    best = 0.0
    job_tokens = _tokens(job_title)
    for title in titles:
        if not title:
            continue
        title_lower = title.lower()
        if title_lower == job_title:
            return 100.0
        if title_lower in job_title or job_title in title_lower:
            best = max(best, 85.0)
            continue
        overlap = job_tokens & _tokens(title_lower)
        if overlap:
            ratio = len(overlap) / max(len(job_tokens), 1)
            best = max(best, round(40.0 + ratio * 60.0, 1))
    return best if best else 35.0


def _tokens(text: str) -> set[str]:
    return {token for token in _TOKEN.findall(text) if len(token) > 2}
