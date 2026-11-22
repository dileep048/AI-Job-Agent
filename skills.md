# AI Job Agent — Engineering Skills & Project Playbook

## 1. Project Overview

AI Job Agent is an AI-powered job-search and application SaaS.

The long-term workflow is:

```text
Candidate Profile
      ↓
Job Discovery
      ↓
Job Normalization
      ↓
Deduplication
      ↓
Job Matching
      ↓
Resume Customization
      ↓
Application Q&A
      ↓
Application Preparation
      ↓
User Approval / Automation Rules
      ↓
Supported Application Flow
      ↓
Submission Verification
      ↓
Application Tracking
      ↓
Analytics
```

The product should optimize for:

- Application quality
- Candidate-data accuracy
- Reliability
- Transparency
- Security

It should not optimize only for the number of applications submitted.

---

# 2. Product Roadmap

## Sprint 1 — Foundation

- Project structure
- Docker
- PostgreSQL
- FastAPI
- Next.js
- Authentication
- Candidate profile
- Skills
- Experience
- Education
- Resume upload
- Resume metadata
- Basic dashboard

## Sprint 2 — Job Discovery

- Job sources
- Job ingestion
- Job normalization
- Job deduplication
- Job storage
- Job search UI

## Sprint 3 — Job Matching

- Requirement extraction
- Skill matching
- Experience matching
- Location matching
- Salary matching
- Semantic matching
- Match score
- AI explanation

## Sprint 4 — Resume & Application Preparation

- Resume parsing
- Structured resume
- Tailored resume generation
- Cover letters
- Application questions
- Answer generation
- Application plan

## Sprint 5 — Browser Automation

- Playwright
- Browser manager
- ATS adapters
- Form extraction
- Form filling
- Validation
- Browser sessions

## Sprint 6 — Submission & Verification

- User approval
- Auto-approval rules
- Submission
- Confirmation detection
- Screenshot/audit trail
- Failed application recovery

## Sprint 7 — Automation

- Scheduled discovery
- Daily application limits
- Automated matching
- Notifications
- Analytics
- Agent activity

Do not implement future sprint functionality unless explicitly requested.

---

# 3. Technology Stack

## Frontend

- Next.js latest stable
- TypeScript
- App Router
- Tailwind CSS
- React Hook Form
- Zod
- TanStack Query

## Backend

- Python 3.12+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- psycopg
- pytest
- Ruff
- mypy where practical

## Infrastructure

- Docker
- Docker Compose
- Redis

## Future Infrastructure

- Celery or Temporal
- AWS S3
- pgvector
- Playwright
- Sentry
- Terraform
- GitHub Actions

Do not introduce future infrastructure prematurely.

---

# 4. Repository Structure

Preferred structure:

```text
ai-job-agent/
│
├── AGENTS.md
├── skills.md
├── README.md
├── docker-compose.yml
├── .env.example
├── .gitignore
├── Makefile
│
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── config/
│   │   │   ├── api/
│   │   │   │   └── v1/
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   ├── services/
│   │   │   ├── repositories/
│   │   │   ├── security/
│   │   │   └── utils/
│   │   ├── alembic/
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── web/
│       ├── app/
│       ├── components/
│       ├── hooks/
│       ├── lib/
│       ├── providers/
│       ├── stores/
│       ├── types/
│       ├── public/
│       ├── package.json
│       └── Dockerfile
│
├── infrastructure/
│   └── docker/
│
├── storage/
│
└── docs/
```

The exact structure may evolve, but maintain clear separation of concerns.

---

# 5. Backend Architecture

Use a modular monolith.

Preferred flow:

```text
HTTP Request
     ↓
FastAPI Router
     ↓
Pydantic Schema
     ↓
Service
     ↓
Repository
     ↓
SQLAlchemy
     ↓
PostgreSQL
```

Responsibilities:

### Router

- HTTP concerns
- Authentication dependency
- Request/response handling
- Status codes

### Schema

- Input validation
- Output serialization
- API contracts

### Service

- Business rules
- State transitions
- Orchestration

### Repository

- Database queries
- Persistence operations

### Model

- Database structure
- Relationships
- Constraints

Do not put significant business logic into routers.

---

# 6. Configuration

Use typed settings.

Environment variables should contain:

```env
APP_NAME=AI Job Agent
APP_ENV=development

DATABASE_URL=postgresql+psycopg://postgres:postgres@postgres:5432/job_agent

JWT_SECRET_KEY=change-me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=./storage

CORS_ORIGINS=http://localhost:3000
```

Never commit real secrets.

---

# 7. Database Principles

PostgreSQL is the canonical source of truth.

Use UUID primary keys.

Use foreign keys.

Use appropriate indexes.

Use constraints to enforce data integrity.

Use timestamps on persistent entities.

Prefer normalized relational data for core entities.

Use JSONB for flexible structures such as:

- Resume structured content
- Job raw source data
- Candidate preference arrays
- AI metadata

Do not put the entire application data model into JSONB.

---

# 8. Core Database Entities

Initial entities:

```text
users
candidate_profiles
candidate_skills
experiences
educations
resumes
```

Future entities:

```text
job_sources
jobs
job_skills
job_matches
applications
application_questions
agent_runs
agent_actions
automation_settings
```

---

# 9. User Model

Conceptually:

```text
User
 ├── Candidate Profile
 ├── Resumes
 ├── Applications
 ├── Agent Runs
 └── Automation Settings
```

A user owns all of their resources.

Always enforce ownership in backend queries.

---

# 10. Candidate Profile

Candidate profile should contain:

```text
headline
summary
years_experience
current_role
current_company
preferred_locations
preferred_job_types
minimum_salary
maximum_salary
salary_currency
remote_preference
```

Profile data should be structured enough for future AI matching.

---

# 11. Skills

Skills should be separate entities.

Example:

```text
Python
Backend
5 years
Expert
```

Recommended fields:

```text
skill_name
skill_type
years_experience
proficiency
```

Prevent duplicate skills for the same profile.

---

# 12. Experience

Experience should contain:

```text
company
job_title
start_date
end_date
description
achievements
technologies
```

Current jobs can use:

```text
end_date = NULL
```

Achievements should be stored individually where practical.

---

# 13. Education

Education should support:

```text
institution
degree
field_of_study
start_date
end_date
description
```

Keep education separate from experience.

---

# 14. Resume Architecture

The resume system has two layers:

```text
Uploaded File
     +
Structured Resume Data
```

The structured resume is the canonical content.

Example:

```json
{
  "summary": "...",
  "skills": [],
  "experience": [],
  "education": [],
  "projects": []
}
```

Uploaded PDF/DOCX files are source documents, not the long-term source of truth.

Future AI resume generation must use verified candidate information.

---

# 15. Storage Abstraction

Use:

```text
StorageService
```

Expected operations:

```text
upload
download
delete
get_url
```

Implement local storage first.

Design for future:

```text
LocalStorage
S3Storage
```

Do not couple application logic directly to filesystem operations.

---

# 16. Authentication

Use secure password hashing.

Use JWT authentication initially.

Authentication components:

```text
security/
├── password.py
├── jwt.py
└── dependencies.py
```

Endpoints:

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
GET  /api/v1/auth/me
```

Never return password hashes.

Never log credentials or tokens.

---

# 17. Authorization

Every user-owned endpoint must verify ownership.

Bad:

```python
repository.get(resume_id)
```

Preferred:

```python
repository.get_by_id_and_user(
    resume_id,
    current_user.id
)
```

The frontend must never be responsible for enforcing authorization.

---

# 18. API Design

Use:

```text
/api/v1/
```

Resource-oriented APIs.

Examples:

```text
/api/v1/profile
/api/v1/profile/skills
/api/v1/profile/experience
/api/v1/profile/education
/api/v1/resumes
```

Use correct HTTP semantics.

Return consistent error objects.

---

# 19. Error Handling

Use:

```json
{
  "error": {
    "code": "PROFILE_NOT_FOUND",
    "message": "Candidate profile not found"
  }
}
```

Do not expose:

- stack traces
- SQL errors
- secrets
- internal paths
- tokens
- implementation details

Log useful diagnostic information server-side.

---

# 20. Resume Upload Security

Initially support:

```text
PDF
DOCX
```

Maximum file size:

```text
10 MB
```

Validate:

- extension
- MIME type
- size
- filename

Generate safe storage filenames.

Do not trust client-provided file paths.

Never allow path traversal.

Future storage should use S3/object storage.

---

# 21. Frontend Architecture

Use Next.js App Router.

Preferred routes:

```text
/login
/register

/dashboard
/dashboard/profile
/dashboard/profile/skills
/dashboard/profile/experience
/dashboard/profile/education
/dashboard/resumes
/dashboard/resumes/[id]
/dashboard/jobs
/dashboard/applications
/dashboard/agent
/dashboard/settings
```

Jobs, applications, and agent pages can remain placeholders until their sprint.

---

# 22. Frontend Components

Organize reusable components:

```text
components/
├── ui/
├── forms/
├── layout/
├── profile/
├── resume/
├── dashboard/
├── jobs/
├── applications/
└── agent/
```

Avoid giant page components.

---

# 23. Frontend API Client

Do not scatter raw API requests across components.

Use:

```text
lib/api/
├── client.ts
├── auth.ts
├── profile.ts
├── resume.ts
├── jobs.ts
└── applications.ts
```

Use typed request/response models.

Handle:

```text
401
403
404
409
422
500
```

consistently.

---

# 24. Forms

Use:

```text
React Hook Form
+
Zod
```

Validate on the frontend for UX.

Validate again on the backend for security and correctness.

Never rely only on frontend validation.

---

# 25. UI Principles

The application should feel like a modern AI SaaS product.

Use:

- White background
- Clean cards
- Subtle borders
- Consistent spacing
- Readable typography
- Responsive design
- Accessible controls

Avoid unnecessary visual complexity.

Every major component should have:

```text
Loading
Empty
Error
Success
```

states where applicable.

---

# 26. AI Architecture

Do not create one giant autonomous agent.

Use specialized agents/services:

```text
Discovery Agent
Matching Agent
Resume Agent
Q&A Agent
Application Agent
Verification Agent
```

Coordinate them through an orchestrator/workflow layer when needed.

Use normal application code for deterministic rules.

Use AI for semantic reasoning.

---

# 27. AI Output Rules

When an AI response feeds application logic, prefer structured output.

Example:

```json
{
  "score": 91,
  "recommendation": "APPLY",
  "matched_skills": ["Python", "AWS"],
  "missing_skills": ["Kafka"],
  "explanation": "Strong backend and cloud alignment."
}
```

Avoid depending on arbitrary natural-language output.

Validate AI-generated structured responses before using them.

---

# 28. Candidate Truth Rules

AI must never fabricate candidate facts.

Never invent:

```text
Company
Job title
Dates
Skills
Education
Certification
Achievement
Responsibility
Salary
```

If information is missing, mark it missing.

Future resume generation should follow:

```text
Verified Candidate Data
        ↓
Relevant Evidence
        ↓
AI Rewriting
        ↓
Validation
        ↓
Final Resume
```

---

# 29. Future Matching Architecture

Matching should be hybrid:

```text
Hard Filters
     ↓
Structured Scoring
     ↓
Semantic Similarity
     ↓
LLM Reasoning
     ↓
Final Match
```

Potential dimensions:

```text
Skills
Experience
Title
Location
Salary
Job Type
Candidate Preferences
```

Avoid arbitrary LLM-only scoring.

---

# 30. Future Job Discovery

Job ingestion should eventually support adapters:

```text
JobSource
   ├── Greenhouse
   ├── Lever
   ├── CompanyCareerPage
   └── OtherSupportedSources
```

Normalize all sources into the canonical `jobs` model.

Store source-specific raw data separately.

Use stable external IDs and content hashes for deduplication.

Do not make one source's format the canonical internal format.

---

# 31. Future Application Architecture

Create an application plan before browser execution.

Conceptually:

```json
{
  "job": {},
  "match": {},
  "resume": {},
  "cover_letter": {},
  "questions": [],
  "browser_actions": [],
  "approval_state": "pending"
}
```

This enables:

```text
Manual Apply
AI Prepare
AI Auto Apply
```

without duplicating the entire application workflow.

---

# 32. Application State Machine

Future application states:

```text
discovered
matched
preparing
ready_for_review
approved
applying
submitted
screening
interview
offer
rejected
withdrawn
failed
```

Do not randomly change status values throughout the codebase.

Centralize valid state transitions.

---

# 33. Future Playwright Architecture

When browser automation is introduced:

```text
Application Agent
       ↓
Browser Manager
       ↓
Provider Adapter
       ↓
ATS-specific implementation
```

Example:

```text
browser/
├── manager.py
├── session.py
├── selectors.py
├── forms.py
└── providers/
    ├── base.py
    ├── greenhouse.py
    ├── lever.py
    └── generic.py
```

Use semantic selectors where possible:

```text
label
name
aria-label
placeholder
role
nearby text
```

Avoid fragile positional selectors.

---

# 34. Browser Safety

Browser automation must:

- Operate only on approved application flows.
- Read and fill expected fields.
- Validate data before submission.
- Verify submission success.
- Record important actions.
- Pause on unexpected authentication.
- Pause on CAPTCHA.
- Pause on MFA.
- Pause on sensitive questions when configured.

Never bypass CAPTCHA or anti-bot protections.

Never access unrelated accounts or websites.

Never mark an application submitted without verification.

---

# 35. Human-in-the-Loop

Support:

```text
Manual
Review
Auto
```

Sensitive questions should support mandatory review.

Examples:

```text
Work authorization
Visa sponsorship
Salary expectations
Relocation
Legal declarations
Sensitive demographic questions
```

Do not blindly submit sensitive information.

---

# 36. Agent Observability

Future agent execution should be persisted.

Use:

```text
agent_runs
agent_actions
```

An agent activity stream should eventually look like:

```text
10:32  Searching jobs
10:33  Found 127 jobs
10:35  Analyzing matches
10:37  18 jobs matched
10:40  Preparing application
10:41  Resume customized
10:42  Opening application
10:43  Application submitted
```

Do not log secrets or sensitive candidate information.

---

# 37. Background Jobs

Long-running tasks must not block FastAPI.

Future architecture:

```text
FastAPI
   ↓
Redis
   ↓
Worker
```

Potential tasks:

```text
Job discovery
Job parsing
Matching
Resume generation
Application preparation
Browser automation
Notifications
```

Separate browser workers from normal workers when browser automation becomes significant.

---

# 38. Browser Worker Isolation

Future architecture:

```text
Redis
 ├── General Worker Queue
 │     ├── Matching
 │     ├── Resume
 │     └── Notifications
 │
 └── Browser Worker Queue
       ├── Playwright
       └── Application Automation
```

Browser sessions are resource-heavy and should not compete directly with API workloads.

---

# 39. Testing Strategy

Test:

### Authentication

```text
Register
Duplicate email
Login
Wrong password
Current user
Unauthorized access
```

### Authorization

```text
User A cannot access User B's profile
User A cannot access User B's resume
User A cannot access User B's file
```

### Profile

```text
Create
Read
Update
Delete
```

### Skills

```text
Create
Update
Delete
Duplicate handling
```

### Experience

```text
Create
Update
Delete
Current employment
```

### Education

```text
Create
Update
Delete
```

### Resume

```text
PDF upload
DOCX upload
Invalid file
Oversized file
List
Delete
Set default
Download ownership
```

---

# 40. Code Quality

Python:

- Type hints
- Small functions
- Clear naming
- Dependency injection
- Ruff
- pytest
- SQLAlchemy 2.x style

TypeScript:

- Strict mode
- Typed API models
- Reusable components
- No unnecessary `any`
- Clear server/client boundaries

Avoid premature abstractions.

---

# 41. Git Practices

Use focused commits:

```text
feat: add candidate profile API
feat: add resume upload
fix: prevent cross-user resume access
test: add profile authorization tests
refactor: extract profile repository
```

Never commit:

```text
.env
credentials
API keys
JWT secrets
local databases
large generated files
```

---

# 42. Development Workflow

Before implementing:

1. Inspect repository.
2. Read `AGENTS.md`.
3. Read relevant sections of `skills.md`.
4. Inspect existing implementation.
5. Identify affected files.
6. Plan the smallest correct change.

During implementation:

1. Follow existing conventions.
2. Keep scope focused.
3. Avoid unrelated refactoring.
4. Add validation.
5. Add authorization.
6. Add tests.

After implementation:

1. Run tests.
2. Run linting.
3. Run type checks where applicable.
4. Run frontend build where applicable.
5. Verify migrations.
6. Fix errors.
7. Update documentation if needed.

---

# 43. No Fake Implementations

Never fake:

```text
Job discovery
Match scores
AI analysis
Resume generation
Application submission
Interview status
```

If a feature is not implemented, make that explicit.

Do not create misleading demo data in production paths.

---

# 44. Scalability Strategy

Start simple:

```text
Next.js
+
FastAPI
+
PostgreSQL
+
Redis
+
Worker
```

Scale only when required.

Future AWS architecture may use:

```text
CloudFront
     ↓
Next.js
     ↓
ALB
     ↓
FastAPI
     ↓
RDS PostgreSQL
     +
ElastiCache Redis
     +
S3
     +
Worker Fleet
     +
Browser Worker Fleet
```

Do not introduce Kubernetes unless there is a demonstrated need.

---

# 45. Performance Principles

Prefer:

- Database indexes
- Pagination
- Selective queries
- Async I/O where appropriate
- Caching for expensive repeated reads
- Background processing for long tasks

Avoid:

- N+1 database queries
- Blocking browser operations in API requests
- Loading large datasets unnecessarily
- Repeated LLM calls when deterministic logic is sufficient

---

# 46. Privacy Principles

Candidate data is highly important product data.

Minimize unnecessary storage.

Do not expose resume contents unnecessarily.

Do not log sensitive application answers.

Use access controls for all candidate-owned resources.

Future production deployment should use encryption in transit and at rest.

---

# 47. API Documentation

FastAPI should expose OpenAPI/Swagger during development.

Expected:

```text
GET /docs
GET /openapi.json
```

Document important request/response schemas.

---

# 48. Health & Readiness

Implement:

```text
GET /health
GET /ready
```

Health should indicate that the API process is alive.

Readiness should eventually verify required dependencies such as PostgreSQL.

Do not make health checks unnecessarily expensive.

---

# 49. Docker Development

Development environment should eventually support:

```text
postgres
redis
api
web
```

Use health checks.

Avoid hardcoding environment-specific secrets.

Make local setup easy:

```bash
cp .env.example .env
docker compose up --build
```

Expected development URLs:

```text
Frontend: http://localhost:3000
API:      http://localhost:8000
Swagger:  http://localhost:8000/docs
```

---

# 50. Definition of Done

A feature is complete when:

```text
Implementation
     ↓
Validation
     ↓
Authorization
     ↓
Database migration if required
     ↓
API
     ↓
Frontend
     ↓
Tests
     ↓
Lint
     ↓
Build
     ↓
Documentation
```

Do not call a feature complete merely because the happy-path UI works.

---

# 51. Current Sprint Boundary

The user will explicitly state the current sprint/task.

Only implement that scope.

For example:

```text
Sprint 1
```

should not result in implementation of:

```text
Job scraping
AI matching
Playwright
Auto-apply
```

unless explicitly requested.

---

# 52. Architectural Decision Rule

When choosing between two implementations:

1. Prefer existing project conventions.
2. Prefer simple solutions.
3. Prefer secure solutions.
4. Prefer testable solutions.
5. Prefer replaceable integrations.
6. Avoid premature abstraction.
7. Avoid premature infrastructure.
8. Preserve future compatibility.

The goal is:

```text
Simple
+
Correct
+
Secure
+
Maintainable
+
Ready to evolve
```

---

# 53. Final Product Principle

AI Job Agent should become a reliable personal job assistant.

The key loop is:

```text
Understand Candidate
       ↓
Understand Job
       ↓
Determine Fit
       ↓
Prepare High-quality Application
       ↓
Execute Reliably
       ↓
Verify
       ↓
Track
```

Every future feature should strengthen this loop.
