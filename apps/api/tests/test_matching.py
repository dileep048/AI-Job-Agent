from datetime import date

from app.models.experience import Experience
from app.models.profile import CandidateProfile
from app.models.skill import CandidateSkill
from app.services.matching.requirements import extract_requirements
from app.services.matching.scoring import score_match
from app.services.matching.skills import normalize_skill, skills_match


def test_extract_years_and_known_skills() -> None:
    req = extract_requirements(
        title="Senior Backend Engineer",
        description="Need 5+ years of experience with Python, FastAPI, and AWS. PostgreSQL required.",
        structured_skills=["Kafka"],
        location="Bengaluru",
        locations=[],
        workplace_type="hybrid",
        employment_type="full_time",
        experience_level="senior",
        salary_min=None,
        salary_max=None,
        salary_currency=None,
    )
    assert req.years_required == 5
    names = {normalize_skill(item) for item in req.skills}
    assert "python" in names
    assert "kafka" in names
    assert "aws" in names


def test_skill_aliases() -> None:
    assert skills_match("JavaScript", "JS")
    assert skills_match("PostgreSQL", "Postgres")
    assert not skills_match("Kafka", "Python")


def test_scores_prefer_overlapping_profile() -> None:
    profile = CandidateProfile(
        headline="Backend engineer",
        summary="Builds Python APIs on AWS",
        years_experience=6,
        current_role="Senior Engineer",
        preferred_locations=["Bengaluru"],
        preferred_job_types=["full_time"],
        minimum_salary=2000000,
        maximum_salary=4000000,
        salary_currency="INR",
        remote_preference="hybrid",
    )
    skills = [CandidateSkill(skill_name="Python"), CandidateSkill(skill_name="AWS")]
    experiences = [
        Experience(
            company_name="Acme",
            job_title="Backend Engineer",
            start_date=date(2019, 1, 1),
            description="Python FastAPI services",
            technologies=["FastAPI", "PostgreSQL"],
        )
    ]
    requirements = extract_requirements(
        title="Backend Engineer",
        description="Python and AWS. 4 years of experience. FastAPI.",
        structured_skills=["Python", "AWS"],
        location="Bengaluru",
        locations=[],
        workplace_type="hybrid",
        employment_type="full_time",
        experience_level=None,
        salary_min=2500000,
        salary_max=3500000,
        salary_currency="INR",
    )
    scores = score_match(
        profile=profile,
        skills=skills,
        experiences=experiences,
        requirements=requirements,
        job_title="Backend Engineer",
        job_description="Python FastAPI AWS Bengaluru",
    )
    assert scores.skill >= 90
    assert scores.experience == 100
    assert scores.location == 100
    assert scores.salary == 100
    assert scores.overall >= 70
    assert scores.recommendation in {"APPLY", "CONSIDER"}
    assert "Python" in scores.matched_skills


def test_salary_below_minimum_is_low() -> None:
    profile = CandidateProfile(
        years_experience=5,
        preferred_locations=[],
        preferred_job_types=[],
        minimum_salary=3000000,
        salary_currency="INR",
        remote_preference="remote",
    )
    requirements = extract_requirements(
        title="Engineer",
        description="",
        structured_skills=[],
        location="Remote",
        locations=["Remote"],
        workplace_type="remote",
        employment_type=None,
        experience_level=None,
        salary_min=1000000,
        salary_max=1500000,
        salary_currency="INR",
    )
    scores = score_match(
        profile=profile,
        skills=[],
        experiences=[],
        requirements=requirements,
        job_title="Engineer",
        job_description="",
    )
    assert scores.salary == 20
