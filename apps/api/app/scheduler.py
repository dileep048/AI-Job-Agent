from __future__ import annotations

import logging
import threading
from datetime import UTC
from typing import Any

from app.config import get_settings
from app.db import SessionLocal
from app.services.scheduled_ingestion_service import ScheduledIngestionService

logger = logging.getLogger("ai_job_agent")

_scheduler: Any = None


def parse_ingest_hours(value: str) -> str:
    hours: list[str] = []
    for part in value.split(","):
        part = part.strip()
        if part.isdigit():
            hour = int(part)
            if 0 <= hour <= 23:
                hours.append(str(hour))
    unique = list(dict.fromkeys(hours))
    if len(unique) < 2:
        return "6,18"
    return ",".join(unique[:2])


def run_greenhouse_lever_ingest() -> None:
    db = SessionLocal()
    try:
        ScheduledIngestionService(db).ingest_greenhouse_and_lever()
    except Exception:
        logger.exception("scheduled greenhouse/lever ingest failed")
    finally:
        db.close()


def start_job_ingest_scheduler() -> Any:
    global _scheduler
    settings = get_settings()
    if not settings.job_ingest_scheduler_enabled:
        return None
    if _scheduler is not None:
        return _scheduler

    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        logger.error(
            "apscheduler is not installed; job ingest scheduler disabled. "
            "Rebuild the API image or pip install apscheduler==3.10.4"
        )
        return None

    hours = parse_ingest_hours(settings.job_ingest_hours)
    scheduler = BackgroundScheduler(timezone=UTC)
    scheduler.add_job(
        run_greenhouse_lever_ingest,
        CronTrigger(hour=hours, minute=0, timezone=UTC),
        id="greenhouse_lever_ingest",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
    _scheduler = scheduler
    logger.info("job ingest scheduler started hours=%s UTC", hours)
    if settings.job_ingest_run_on_startup:
        threading.Thread(
            target=run_greenhouse_lever_ingest,
            daemon=True,
            name="job-ingest-startup",
        ).start()
        logger.info("job ingest startup run queued")
    return scheduler


def stop_job_ingest_scheduler() -> None:
    global _scheduler
    if _scheduler is None:
        return
    _scheduler.shutdown(wait=False)
    _scheduler = None
