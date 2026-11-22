from app.services.matching.dto import JobRequirements, MatchResult


def build_explanation(result: MatchResult, requirements: JobRequirements) -> str:
    parts = [
        f"Overall fit is {result.score:.0f}/100 ({result.recommendation}).",
        f"Skills {result.skill_score:.0f}/100 with {len(result.matched_skills)} required matches.",
    ]
    if result.missing_skills:
        parts.append(f"Missing required skills: {', '.join(result.missing_skills[:8])}.")
    if requirements.minimum_years_experience is not None:
        parts.append(
            f"Experience score {result.experience_score:.0f}/100 against "
            f"{requirements.minimum_years_experience}+ years required."
        )
    if result.strengths:
        parts.append("Strengths: " + "; ".join(result.strengths[:3]) + ".")
    if result.concerns:
        parts.append("Concerns: " + "; ".join(result.concerns[:3]) + ".")
    parts.append("Scores use verified profile data only.")
    return " ".join(parts)
