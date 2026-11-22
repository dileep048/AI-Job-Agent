# AI Job Agent

Production-ready foundation for a SaaS product that will eventually find jobs, score matches, customize resumes, and apply through supported flows.

Sprint 1 delivers the monorepo, authentication, candidate profile, skills, experience, education, resume storage, and a dashboard UI. Job scraping, AI agents, Playwright, and auto-apply are **not** included.

## Architecture

```
Browser (Next.js)
    ↓
REST /api/v1 (FastAPI)
    ↓
Services → Repositories → SQLAlchemy
    ↓
PostgreSQL

Resume files → StorageService (local now, S3 later)
Redis is provisioned for future workers only.
```

## Tech stack

| Layer | Stack |
| --- | --- |
| Frontend | Next.js (App Router), TypeScript, Tailwind CSS, React Hook Form, Zod, TanStack Query |
| Backend | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, psycopg |
| Auth | JWT access + refresh tokens, Argon2 password hashing |
| Data | PostgreSQL 16 |
| Infra | Docker Compose, Redis (unused in app code) |

## Prerequisites

- Docker Desktop (or Docker Engine + Compose)
- Optional for host development: Python 3.12+, Node.js 22+

## Environment setup

```bash
cp .env.example .env
```

Never commit `.env`. Rotate `JWT_SECRET_KEY` before any non-local use.

## Running locally (Docker)

```bash
cp .env.example .env
docker compose up --build
```

Then:

- Frontend: http://localhost:3000
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health: http://localhost:8000/health

Useful Make targets:

```bash
make up
make down
make logs
make migrate
make test
make lint
```

The API container runs `alembic upgrade head` on startup.

## Running services independently

### API

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/job_agent
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Web

```bash
cd apps/web
npm install
export NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

PostgreSQL must already be running (Compose `postgres` service is enough).

## Database migrations

```bash
docker compose exec api alembic upgrade head
docker compose exec api alembic revision --autogenerate -m "describe change"
```

Initial migration creates:

- `users`
- `candidate_profiles`
- `candidate_skills`
- `experiences`
- `educations`
- `resumes`

Sprint 2 migration `0002_jobs` adds `job_sources`, `jobs`, and `job_skills`.
Migration `0003_job_fetch_schedule` adds `current_fetch_datetime` / `last_fetch_datetime` on `job_sources` and a `job_fetch_runs` table.

## Testing

```bash
docker compose exec api pytest -q
```

From the API folder with a reachable Postgres:

```bash
cd apps/api
pytest -q
```

Tests create a `job_agent_test` database.

Frontend:

```bash
cd apps/web
npm run lint
npm run build
```

## API documentation

Interactive OpenAPI docs live at `/docs`. Versioned application routes are under `/api/v1`.

### Auth

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/refresh`

### Profile

- `GET|POST|PUT|DELETE /api/v1/profile`
- Skills, experience, and education nested under `/api/v1/profile/...`

### Resumes

- `GET|POST /api/v1/resumes`
- `POST /api/v1/resumes/upload`
- `GET|PUT|DELETE /api/v1/resumes/{id}`
- `GET /api/v1/resumes/{id}/download`
- `POST /api/v1/resumes/{id}/set-default`

Error bodies:

```json
{
  "error": {
    "code": "PROFILE_NOT_FOUND",
    "message": "Candidate profile not found"
  }
}
```

## Project structure

```text
apps/api/     FastAPI backend
apps/web/     Next.js frontend
storage/      Local file storage (gitignored contents)
infrastructure/docker/
docs/
```

Storage is abstracted behind `StorageService` (`upload`, `download`, `delete`, `get_url`). Resume PDFs/DOCX are not the source of truth; `resumes.resume_data` JSON is.

## Sprint 2 — Job discovery

Jobs are **global catalog records**, not user-owned. Authenticated users can search, create, update, delete, and ingest. Candidate profile/resume ownership rules from Sprint 1 are unchanged.

### Database

- `job_sources` — adapter type, optional config JSON, active flag
- `jobs` — normalized listing + `raw_data` + `content_hash`
- `job_skills` — unique `(job_id, skill_name)`

Dedup: `source_id + external_id`, then `content_hash` of company, title, location, and description.

### Job APIs

- `GET /api/v1/jobs` — search (`q`, `location`, `workplace_type`, `employment_type`, `company`, `experience_level`, `salary_min`, `salary_max`, `is_active`, `source`, `page`, `page_size`)
- `GET /api/v1/jobs/{job_id}`
- `POST /api/v1/jobs` — authenticated manual create
- `POST /api/v1/jobs/from-url` — import a Greenhouse or Lever job or board URL
- `PATCH /api/v1/jobs/{job_id}`
- `DELETE /api/v1/jobs/{job_id}`
- `POST /api/v1/jobs/ingest` — fetch via adapter, normalize, upsert (`url` also accepted)
- `POST /api/v1/jobs/ingest/boards` — fetch all configured Greenhouse and Lever boards
- `GET /api/v1/jobs/fetch-runs/latest` — last catalog fetch timestamps and counts
- `GET /api/v1/job-sources`
- `POST /api/v1/job-sources` — add a Greenhouse/Lever board by URL or slug
- `PATCH /api/v1/job-sources/{source_id}` — enable/disable

### Supported sources

| Type | How |
| --- | --- |
| `manual` | `configuration.jobs` array on ingest, or `POST /jobs` |
| `greenhouse` | Public `boards-api.greenhouse.io` with `board_token` |
| `lever` | Public `api.lever.co/v0/postings/{site}` |

### Run ingestion

```bash
curl -X POST http://localhost:8000/api/v1/jobs/ingest \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"source_type":"manual","configuration":{"jobs":[{"title":"Backend Engineer","company_name":"Acme","location":"Bengaluru"}]}}'
```

Greenhouse example:

```json
{"source_type":"greenhouse","configuration":{"board_token":"YOUR_BOARD","company_name":"Acme"}}
```

### Scheduled Greenhouse + Lever fetch

There is no public “all jobs on Greenhouse/Lever” index. The app keeps a catalog of public board slugs, plus any extras in `GREENHOUSE_BOARD_TOKENS` and `LEVER_SITES`, and pulls **every listing on each of those boards** through the official public APIs.

Twice a day at **06:00 and 18:00 UTC** (configurable via `JOB_INGEST_HOURS`) the API:

1. Writes `current_fetch_datetime` and `last_fetch_datetime` on the fetch run and on each board
2. Fetches jobs
3. Upserts into PostgreSQL (idempotent)

Enable the scheduler with `JOB_INGEST_SCHEDULER_ENABLED=true` (set in Docker Compose). Trigger immediately:

```bash
make ingest
```

or

```bash
curl -X POST http://localhost:8000/api/v1/jobs/ingest/boards \
  -H "Authorization: Bearer $TOKEN"
```

Add more companies as comma-separated slugs:

```bash
GREENHOUSE_BOARD_TOKENS=stripe,anthropic
LEVER_SITES=netflix,gusto
```

Dashboard: **Jobs** for search and “Fetch Greenhouse & Lever now”; **Settings** shows current/last fetch times.

### Add a new job source

1. Implement `JobSourceAdapter.fetch_jobs()` under `apps/api/app/services/jobs/sources/`.
2. Register it in `sources/registry.py`.
3. Map source-native fields into the shared dict the normalizer expects (`title`, `company_name`, …).
4. Do not scrape arbitrary sites or add Playwright here.

## Future roadmap

- Sprint 3: AI matching and resume customization
- Sprint 4: application plans and questions
- Sprint 5: Playwright workers and ATS adapters
