from __future__ import annotations

from app.services.matching.dto import CandidateEvidence, JobRequirements


def match_experience(candidate: CandidateEvidence, requirements: JobRequirements) -> tuple[float, int | None, int | None]:
    years = candidate.total_years_experience
    required = requirements.minimum_years_experience
    if required is None or years is None:
        return 50.0, years, required
    if years >= required:
        return 100.0, years, required
    if years >= max(required - 1, 0):
        return 75.0, years, required
    return round(max(0.0, 100.0 * years / required), 1), years, required
