from unittest.mock import Mock, patch

from app.services.jobs.sources.greenhouse import GreenhouseJobSourceAdapter
from app.services.jobs.sources.lever import LeverJobSourceAdapter


def test_greenhouse_maps_public_payload() -> None:
    adapter = GreenhouseJobSourceAdapter()
    payload = {
        "jobs": [
            {
                "id": 99,
                "title": "Engineer",
                "absolute_url": "https://example.com/job",
                "content": "<p>Hello</p>",
                "updated_at": "2026-01-01T00:00:00Z",
                "location": {"name": "Remote"},
                "departments": [{"name": "Engineering"}],
                "offices": [{"name": "Bengaluru"}],
            }
        ]
    }
    response = Mock(status_code=200)
    response.json.return_value = payload
    with patch("app.services.jobs.sources.greenhouse.httpx.get", return_value=response):
        jobs = adapter.fetch_jobs({"board_token": "acme", "company_name": "Acme"})
    assert len(jobs) == 1
    assert jobs[0]["external_id"] == "99"
    assert jobs[0]["source_url"] == "https://example.com/job"


def test_greenhouse_fetches_single_job() -> None:
    adapter = GreenhouseJobSourceAdapter()
    response = Mock(status_code=200)
    response.json.return_value = {"id": 7, "title": "Staff Engineer", "content": "Go"}
    with patch("app.services.jobs.sources.greenhouse.httpx.get", return_value=response) as get:
        jobs = adapter.fetch_jobs({"board_token": "acme", "job_id": "7"})
    assert jobs[0]["external_id"] == "7"
    assert "/jobs/7" in get.call_args.args[0]


def test_lever_maps_public_payload() -> None:
    adapter = LeverJobSourceAdapter()
    payload = [
        {
            "id": "abc",
            "text": "Designer",
            "hostedUrl": "https://jobs.lever.co/acme/abc",
            "descriptionPlain": "Design things",
            "createdAt": 1700000000000,
            "categories": {"location": "NYC", "commitment": "full-time", "team": "Design"},
        }
    ]
    response = Mock(status_code=200)
    response.json.return_value = payload
    with patch("app.services.jobs.sources.lever.httpx.get", return_value=response):
        jobs = adapter.fetch_jobs({"site": "acme", "company_name": "Acme"})
    assert jobs[0]["title"] == "Designer"
    assert jobs[0]["employment_type"] == "full-time"


def test_missing_board_skipped_when_configured() -> None:
    adapter = GreenhouseJobSourceAdapter()
    response = Mock(status_code=404)
    with patch("app.services.jobs.sources.greenhouse.httpx.get", return_value=response):
        jobs = adapter.fetch_jobs({"board_token": "missing", "skip_http_errors": True})
    assert jobs == []
