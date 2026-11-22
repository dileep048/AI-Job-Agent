from __future__ import annotations

from app.services.matching.dto import CandidateEvidence, JobRequirements
from app.services.matching.semantic import cosine_similarity


def match_semantic(
    candidate: CandidateEvidence,
    requirements: JobRequirements,
    job_description: str | None,
) -> float:
    profile_text = " ".join(
        [
            candidate.headline or "",
            candidate.summary or "",
            candidate.current_title or "",
            *candidate.skills,
            *[
                f"{item.get('job_title', '')} {item.get('description', '')} "
                f"{' '.join(str(t) for t in item.get('technologies', []))}"
                for item in candidate.experiences
            ],
        ]
    )
    job_text = f"{requirements.title} {job_description or ''}"
    return round(cosine_similarity(profile_text, job_text) * 100.0, 1)
