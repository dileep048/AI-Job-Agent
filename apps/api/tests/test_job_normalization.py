from app.exceptions import ValidationAppError
from app.services.jobs.normalizer import JobNormalizationService

normalizer = JobNormalizationService()


def test_whitespace_and_empty_values() -> None:
    job = normalizer.normalize(
        {
            "title": "  Senior  Backend  ",
            "company_name": " Acme ",
            "description": "   ",
            "location": "",
            "company_url": None,
        }
    )
    assert job.title == "Senior Backend"
    assert job.company_name == "Acme"
    assert job.description is None
    assert job.location is None


def test_employment_and_workplace_normalization() -> None:
    job = normalizer.normalize(
        {
            "title": "Engineer",
            "company_name": "Acme",
            "employment_type": "Full-Time",
            "workplace_type": "Work from home",
        }
    )
    assert job.employment_type == "full_time"
    assert job.workplace_type == "remote"


def test_location_normalization() -> None:
    job = normalizer.normalize(
        {
            "title": "Engineer",
            "company_name": "Acme",
            "location": "Bengaluru",
            "locations": ["Bengaluru", " bengaluru ", "Remote"],
        }
    )
    assert job.location == "Bengaluru"
    assert job.locations == ["Bengaluru", "Remote"]


def test_html_description_decoded_to_plain_text() -> None:
    encoded = (
        "&lt;div class=&quot;content-intro&quot;&gt;&lt;p&gt;Ready to do the most "
        "impactful work of your career? At&amp;nbsp;&lt;a href=&quot;https://www.coinbase.com/"
        "&quot;&gt;Coinbase&lt;/a&gt;, we are uncompromising.&lt;/p&gt;&lt;/div&gt;"
    )
    job = normalizer.normalize(
        {"title": "Engineer", "company_name": "Coinbase", "description": encoded}
    )
    assert job.description is not None
    assert "<" not in job.description
    assert "&lt;" not in job.description
    assert "&amp;" not in job.description
    assert "Ready to do the most impactful work" in job.description
    assert "Coinbase" in job.description


def test_html_tags_become_readable_text() -> None:
    job = normalizer.normalize(
        {
            "title": "Engineer",
            "company_name": "Acme",
            "description": "<p>Build APIs</p><p>Use Python</p>",
        }
    )
    assert job.description == "Build APIs\nUse Python"


def test_raw_data_preserved() -> None:
    raw = {"title": "Engineer", "company_name": "Acme", "extra": {"id": 1}}
    job = normalizer.normalize({**raw, "raw_data": raw})
    assert job.raw_data["extra"]["id"] == 1


def test_required_fields() -> None:
    try:
        normalizer.normalize({"title": "Only title"})
        raise AssertionError("expected validation error")
    except ValidationAppError as exc:
        assert exc.code == "INVALID_JOB"


def test_content_hash_stable() -> None:
    a = normalizer.normalize({"title": "Eng", "company_name": "Acme", "location": "X", "description": "Y"})
    b = normalizer.normalize({"title": "Eng", "company_name": "Acme", "location": "X", "description": "Y"})
    assert normalizer.hash_for(a) == normalizer.hash_for(b)
    c = normalizer.normalize({"title": "Eng", "company_name": "Acme", "location": "X", "description": "Z"})
    assert normalizer.hash_for(a) != normalizer.hash_for(c)
