from __future__ import annotations

from app.services.matching.dto import CandidateEvidence, JobRequirements


def match_location(candidate: CandidateEvidence, requirements: JobRequirements) -> float:
    workplace = (requirements.workplace_type or "").lower()
    preference = (candidate.preferred_workplace_types[0] if candidate.preferred_workplace_types else "")
    job_locations = " ".join(requirements.location_requirements).lower()
    remote_job = workplace == "remote" or "remote" in job_locations
    preferred = [item.lower() for item in candidate.preferred_locations if item]

    if remote_job and preference in {"remote", "hybrid", "flexible", "any", ""}:
        return 100.0
    if remote_job and preference == "onsite":
        return 40.0
    if workplace == "onsite" and preference == "remote":
        return 25.0
    if not preferred:
        return 50.0
    if preferred and any(loc in job_locations or job_locations in loc for loc in preferred if loc):
        return 100.0
    if preferred and job_locations:
        return 35.0
    if workplace == "hybrid" and preference in {"hybrid", "remote", "flexible", ""}:
        return 80.0
    return 50.0


def match_workplace(candidate: CandidateEvidence, requirements: JobRequirements) -> float:
    preference = (candidate.preferred_workplace_types[0] if candidate.preferred_workplace_types else "")
    workplace = (requirements.workplace_type or "").lower()
    if not preference or not workplace:
        return 50.0
    if preference == workplace:
        return 100.0
    if preference in {"flexible", "any"}:
        return 90.0
    if {preference, workplace} <= {"remote", "hybrid"}:
        return 75.0
    return 30.0


def match_employment(candidate: CandidateEvidence, requirements: JobRequirements) -> float:
    preferred = candidate.preferred_employment_types
    job_type = requirements.employment_type
    if not preferred or not job_type:
        return 50.0
    normalized = job_type.lower().replace("-", "_").replace(" ", "_")
    if any(normalized in pref or pref in normalized for pref in preferred):
        return 100.0
    return 25.0
