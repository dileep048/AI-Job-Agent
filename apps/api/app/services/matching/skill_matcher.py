from __future__ import annotations

from app.services.matching.dto import CandidateEvidence
from app.services.matching.skills import skills_match


def match_skills(
    candidate: CandidateEvidence,
    required: list[str],
    preferred: list[str] | None = None,
) -> tuple[list[str], list[str], list[str], float]:
    pool = list(candidate.skills)
    for experience in candidate.experiences:
        pool.extend(str(item) for item in experience.get("technologies", []))
    preferred = preferred or []
    matched: list[str] = []
    missing: list[str] = []
    preferred_matched: list[str] = []
    for skill in required:
        if any(skills_match(skill, item) for item in pool):
            matched.append(skill)
        else:
            missing.append(skill)
    for skill in preferred:
        if skill in matched or skill in missing:
            continue
        if any(skills_match(skill, item) for item in pool):
            preferred_matched.append(skill)
    if not required:
        skill_score = 50.0 if not preferred else round(
            100.0 * len(preferred_matched) / max(len(preferred), 1), 1
        )
    else:
        skill_score = round(100.0 * len(matched) / len(required), 1)
    return matched, missing, preferred_matched, skill_score
