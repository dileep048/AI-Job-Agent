.PHONY: up down logs api web migrate ingest migration test lint format

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

api:
	docker compose up api postgres redis --build

web:
	docker compose up web --build

migrate:
	docker compose exec api alembic upgrade head

ingest:
	docker compose exec api python -c "from app.db import SessionLocal; from app.services.scheduled_ingestion_service import ScheduledIngestionService; db=SessionLocal(); ScheduledIngestionService(db).ingest_greenhouse_and_lever(); db.close()"

migration:
	docker compose exec api alembic revision --autogenerate -m "$(m)"

test:
	docker compose exec api pytest -q

lint:
	docker compose exec api ruff check app tests
	docker compose exec web npm run lint

format:
	docker compose exec api ruff format app tests
	docker compose exec web npx prettier --write "app/**/*.{ts,tsx}" "components/**/*.{ts,tsx}" "lib/**/*.{ts,tsx}"
