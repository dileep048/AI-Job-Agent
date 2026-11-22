AI Job Agent — Cursor Instructions

1. Read Project Rules First

Before making any code changes:

Read skills.md.

Inspect the existing repository.

Understand the current implementation before modifying it.

Follow the architecture, security, coding, and product rules in skills.md.

skills.md is the detailed engineering playbook. This file contains the shorter always-follow instructions.

2. Project Goal

AI Job Agent is a SaaS product that helps candidates:

Build and manage a candidate profile.

Upload and manage resumes.

Discover relevant jobs.

Analyze job descriptions.

Score job-candidate fit.

Customize resumes.

Generate application answers.

Prepare applications.

Apply through supported application flows.

Track applications and outcomes.

The long-term product should behave like a reliable AI job assistant, not an unrestricted browser bot.

3. Scope Control

Implement only the sprint/task explicitly requested by the user.

Do not prematurely implement:

Job scraping

AI matching

Resume customization

Playwright automation

Auto-apply

Notifications

Billing

Complex distributed infrastructure

unless the user explicitly requests them.

Do not rewrite unrelated code.

Do not delete existing functionality without explicit approval.

4. Architecture Rules

Prefer a modular monolith during early development.

Backend:

Router
  ↓
Schema
  ↓
Service
  ↓
Repository
  ↓
SQLAlchemy
  ↓
PostgreSQL

Keep:

HTTP concerns in routers.

Validation in schemas.

Business logic in services.

Database queries in repositories.

Database structure in models/migrations.

Do not put large amounts of business logic inside route handlers.

5. Security Rules

Always enforce authenticated user ownership.

A user must never access another user's:

Profile

Skills

Experience

Education

Resume

Uploaded files

Applications

Agent data

Never trust IDs supplied by the frontend.

Never store or log plaintext passwords.

Never expose:

Password hashes

JWT tokens

API keys

Secrets

Stack traces

Internal database errors

Never hardcode secrets.

6. Candidate Data Accuracy

Candidate information is source-of-truth data.

Never invent:

Employment history

Companies

Job titles

Skills

Education

Certifications

Achievements

Dates

Responsibilities

Future AI features may rewrite verified information but must not fabricate qualifications.

7. AI Agent Rules

Do not create one unrestricted "super agent".

Use specialized components where needed:

Discovery Agent
Matching Agent
Resume Agent
Q&A Agent
Application Agent
Verification Agent

Use deterministic application logic for:

Authentication

Authorization

Validation

State transitions

Limits

Database writes

Security

Use AI where semantic reasoning provides value.

Prefer structured AI outputs over free-form text.

8. Browser Automation Rules

When Playwright is introduced:

Use explicit provider/ATS adapters.

Restrict browser actions to approved application flows.

Validate fields before submission.

Verify successful submission.

Record important actions.

Pause for CAPTCHA, MFA, unexpected authentication, or sensitive questions.

Never attempt to bypass CAPTCHA or anti-bot protections.

Never mark an application as submitted unless submission has actually been verified.

9. Coding Standards

Python

Use:

Python 3.12+

Type hints

FastAPI

Pydantic v2

SQLAlchemy 2.x

Alembic

pytest

Ruff

TypeScript

Use:

Strict TypeScript

Next.js App Router

Reusable components

Typed API responses

No unnecessary any

Avoid duplicated business logic.

Prefer simple, readable, maintainable code.

10. Database Rules

PostgreSQL is the canonical source of truth.

Use:

UUID primary keys

Foreign keys

Proper constraints

created_at

updated_at

Use JSONB only when flexible structured data is appropriate.

All schema changes must use Alembic migrations.

11. File Upload Rules

For resume files:

Support PDF and DOCX initially.

Maximum 10 MB.

Validate extension.

Validate MIME type.

Validate file size.

Generate safe internal filenames.

Do not use user-provided filenames as filesystem paths.

Use a storage abstraction so local storage can later be replaced by S3.

12. Frontend Rules

Use:

Next.js

TypeScript

Tailwind CSS

React Hook Form

Zod

TanStack Query

Keep pages and reusable components separate.

Every important UI feature should have:

Loading state

Empty state

Error state

Success feedback

Prefer a clean, professional, predominantly white UI.

13. API Rules

Use versioned APIs:

/api/v1/

Use correct HTTP status codes.

Return consistent errors:

{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message"
  }
}

Do not expose internal implementation details.

14. Development Workflow

For every task:

Inspect
  ↓
Understand
  ↓
Plan
  ↓
Implement
  ↓
Test
  ↓
Lint
  ↓
Build/Verify
  ↓
Summarize

Before editing, identify:

Files to create

Files to modify

Database changes

API changes

Frontend changes

Tests required

After implementation:

Run relevant tests.

Run linting/type checks.

Run frontend build if applicable.

Verify migrations if applicable.

Fix errors.

Summarize what changed.

15. No Fake Implementations

Do not create fake production functionality.

Do not:

Return fake application submissions.

Pretend a job was scraped when it wasn't.

Pretend an application succeeded.

Invent candidate data.

Hide unimplemented functionality behind misleading UI.

If functionality belongs to a future sprint, label it as coming soon or leave it unimplemented.

16. Avoid Overengineering

Do not introduce:

Kubernetes

Kafka

Microservices

Temporal

Elasticsearch

Complex event sourcing

Vector databases

Distributed systems

unless the current requirement genuinely needs them.

Prefer:

Simple + Correct + Maintainable

over:

Complex + Prematurely Scalable

17. Final Rule

The user will define the current sprint/task.

Implement that task completely and correctly while preserving the architecture defined in skills.md.

Never trade security, candidate-data accuracy, or correctness for speed.