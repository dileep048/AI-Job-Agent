from __future__ import annotations

import logging
import time
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.job_fetch_run import JobFetchRun
from app.models.job_source import JobSource
from app.repositories.job_fetch_run_repository import JobFetchRunRepository
from app.repositories.job_source_repository import JobSourceRepository
from app.services.job_ingestion_service import IngestionResult, JobIngestionService
from app.services.jobs.board_catalog import BoardRef, load_board_catalog

logger = logging.getLogger("ai_job_agent")

_LOCK_KEY = 81202329


class ScheduledIngestionService:
    def __init__(
        self,
        db: Session,
        *,
        boards: list[BoardRef] | None = None,
        ingestion: JobIngestionService | None = None,
    ) -> None:
        self.db = db
        self.sources = JobSourceRepository(db)
        self.runs = JobFetchRunRepository(db)
        self.ingestion = ingestion or JobIngestionService(db)
        self.boards = boards if boards is not None else load_board_catalog()
        self.settings = get_settings()

    def ingest_greenhouse_and_lever(self) -> JobFetchRun | None:
        if not self._try_lock():
            logger.info("greenhouse/lever ingest skipped; another run holds the lock")
            return self.runs.get_latest()

        try:
            return self._run()
        finally:
            self._unlock()

    def _run(self) -> JobFetchRun:
        now = datetime.now(UTC)
        previous = self.runs.get_latest()
        run = self.runs.create(
            JobFetchRun(
                current_fetch_datetime=now,
                last_fetch_datetime=previous.current_fetch_datetime if previous else None,
                status="running",
            )
        )
        logger.info(
            "board ingest started current_fetch_datetime=%s last_fetch_datetime=%s",
            run.current_fetch_datetime.isoformat(),
            run.last_fetch_datetime.isoformat() if run.last_fetch_datetime else None,
        )
        self.ensure_catalog_sources()
        sources = self.sources.list_active_boards()
        errors: list[str] = []
        totals = {
            "fetched": 0,
            "inserted": 0,
            "updated": 0,
            "duplicates": 0,
            "failed": 0,
            "boards_succeeded": 0,
        }
        delay = max(self.settings.job_ingest_board_delay_seconds, 0)

        for index, source in enumerate(sources):
            try:
                result = self.ingestion.ingest(
                    source_id=source.id,
                    configuration={"skip_http_errors": True},
                )
                self._add_totals(totals, result)
                totals["boards_succeeded"] += 1
            except Exception:
                totals["failed"] += 1
                errors.append(f"{source.source_type}:{source.external_key}")
                logger.exception(
                    "board ingest failed type=%s key=%s",
                    source.source_type,
                    source.external_key,
                )
            if delay and index < len(sources) - 1:
                time.sleep(delay)

        run.boards_attempted = len(sources)
        run.boards_succeeded = totals["boards_succeeded"]
        run.fetched = totals["fetched"]
        run.inserted = totals["inserted"]
        run.updated = totals["updated"]
        run.duplicates = totals["duplicates"]
        run.failed = totals["failed"]
        run.errors = errors[:50]
        run.status = "completed"
        run.finished_at = datetime.now(UTC)
        self.runs.save(run)
        logger.info(
            "board ingest completed boards=%s fetched=%s inserted=%s updated=%s",
            run.boards_attempted,
            run.fetched,
            run.inserted,
            run.updated,
        )
        return run

    def ensure_catalog_sources(self) -> None:
        for board in self.boards:
            if self.sources.get_by_type_and_key(board.source_type, board.key):
                continue
            self.sources.create(self._source_from_board(board))

    def latest_run(self) -> JobFetchRun | None:
        return self.runs.get_latest()

    def _source_from_board(self, board: BoardRef) -> JobSource:
        if board.source_type == "greenhouse":
            configuration: dict[str, Any] = {
                "board_token": board.key,
                "company_name": board.name,
            }
        else:
            configuration = {"site": board.key, "company_name": board.name}
        return JobSource(
            name=board.name[:128],
            source_type=board.source_type,
            external_key=board.key,
            configuration=configuration,
            is_active=True,
        )

    def _try_lock(self) -> bool:
        locked = self.db.execute(text("SELECT pg_try_advisory_lock(:k)"), {"k": _LOCK_KEY})
        return bool(locked.scalar())

    def _unlock(self) -> None:
        self.db.execute(text("SELECT pg_advisory_unlock(:k)"), {"k": _LOCK_KEY})
        self.db.commit()

    @staticmethod
    def _add_totals(totals: dict[str, int], result: IngestionResult) -> None:
        totals["fetched"] += result.fetched
        totals["inserted"] += result.inserted
        totals["updated"] += result.updated
        totals["duplicates"] += result.duplicates
        totals["failed"] += result.failed
