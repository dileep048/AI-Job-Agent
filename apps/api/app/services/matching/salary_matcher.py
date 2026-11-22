from __future__ import annotations

from app.services.matching.dto import CandidateEvidence, JobRequirements


def match_salary(candidate: CandidateEvidence, requirements: JobRequirements) -> tuple[float, bool | None]:
    job_min = requirements.salary_min
    job_max = requirements.salary_max
    if job_min is None and job_max is None:
        return 50.0, None
    if candidate.minimum_salary is None and candidate.maximum_salary is None:
        return 50.0, None
    if candidate.salary_currency and requirements.salary_currency:
        if candidate.salary_currency.upper() != requirements.salary_currency.upper():
            return 50.0, None
    job_high = job_max if job_max is not None else job_min
    job_low = job_min if job_min is not None else job_max
    if candidate.minimum_salary is not None and job_high is not None and job_high < candidate.minimum_salary:
        return 20.0, False
    if candidate.maximum_salary is not None and job_low is not None and job_low > candidate.maximum_salary:
        return 70.0, True
    return 100.0, True
