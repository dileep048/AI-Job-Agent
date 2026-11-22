import pytest

from app.exceptions import ValidationAppError
from app.services.jobs.url_parser import parse_ats_url, require_ats_url


def test_parse_greenhouse_job_url() -> None:
    parsed = parse_ats_url("https://boards.greenhouse.io/coinbase/jobs/6123695")
    assert parsed is not None
    assert parsed.source_type == "greenhouse"
    assert parsed.key == "coinbase"
    assert parsed.job_id == "6123695"


def test_parse_greenhouse_board_url() -> None:
    parsed = parse_ats_url("https://job-boards.greenhouse.io/stripe")
    assert parsed is not None
    assert parsed.job_id is None
    assert parsed.key == "stripe"


def test_parse_lever_job_and_apply_url() -> None:
    parsed = parse_ats_url("https://jobs.lever.co/acme/abc-123/apply")
    assert parsed is not None
    assert parsed.source_type == "lever"
    assert parsed.key == "acme"
    assert parsed.job_id == "abc-123"


def test_parse_greenhouse_embed_query() -> None:
    parsed = parse_ats_url("https://boards.greenhouse.io/embed/job_app?for=coinbase&token=99")
    assert parsed is not None
    assert parsed.key == "coinbase"
    assert parsed.job_id == "99"


def test_unsupported_url() -> None:
    assert parse_ats_url("https://linkedin.com/jobs/view/123") is None
    with pytest.raises(ValidationAppError) as exc:
        require_ats_url("https://linkedin.com/jobs/view/123")
    assert exc.value.code == "UNSUPPORTED_JOB_URL"
