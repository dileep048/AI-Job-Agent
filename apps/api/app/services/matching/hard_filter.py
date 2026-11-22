from __future__ import annotations

from app.services.matching.dto import CandidateEvidence, HardFilterResult, JobRequirements


def apply_hard_filters(
    candidate: CandidateEvidence, requirements: JobRequirements
) -> HardFilterResult:
    reasons: list[str] = []
    workplace = (requirements.workplace_type or "").lower()
    job_locations = " ".join(requirements.location_requirements).lower()
    remote_job = workplace == "remote" or "remote" in job_locations
    preferred_locations = [loc.lower() for loc in candidate.preferred_locations if loc]

    if preferred_locations and not remote_job and workplace != "hybrid":
        if job_locations and not any(
            loc in job_locations or job_locations in loc for loc in preferred_locations
        ):
            reasons.append("Job location does not match preferred locations")

    if candidate.preferred_employment_types and requirements.employment_type:
        job_type = _norm(requirements.employment_type)
        if not any(job_type in pref or pref in job_type for pref in candidate.preferred_employment_types):
            reasons.append("Employment type does not match preferred job types")

    if candidate.minimum_salary is not None and requirements.salary_max is not None:
        if requirements.salary_currency and candidate.salary_currency:
            if requirements.salary_currency.upper() == candidate.salary_currency.upper():
                if requirements.salary_max < candidate.minimum_salary:
                    reasons.append("Job salary range is below candidate minimum salary")

    if candidate.preferred_workplace_types and requirements.workplace_type:
        pref = set(candidate.preferred_workplace_types)
        job_wp = _norm(requirements.workplace_type)
        if pref == {"remote"} and job_wp == "onsite" and not remote_job:
            reasons.append("Candidate prefers remote work but job is onsite-only")

    return HardFilterResult(passed=len(reasons) == 0, reasons=reasons)


def _norm(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")
