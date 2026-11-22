import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.config import get_settings
from app.db import engine
from app.exceptions import AppError
from app.middleware import RequestIDMiddleware
from app.scheduler import start_job_ingest_scheduler, stop_job_ingest_scheduler
from app.schemas.common import HealthResponse, ReadyResponse
from app.utils.logging import configure_logging

logger = logging.getLogger("ai_job_agent")
settings = get_settings()
configure_logging(settings.app_debug)


@asynccontextmanager
async def lifespan(_application: FastAPI):
    start_job_ingest_scheduler()
    yield
    stop_job_ingest_scheduler()


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    application.add_middleware(RequestIDMiddleware)

    from fastapi.middleware.cors import CORSMiddleware

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router)

    @application.get("/health", response_model=HealthResponse, tags=["ops"])
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @application.get("/ready", response_model=ReadyResponse, tags=["ops"])
    def ready() -> ReadyResponse | JSONResponse:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return ReadyResponse(status="ok", database="ok")
        except SQLAlchemyError:
            logger.exception("Readiness check failed")
            return JSONResponse(
                status_code=503,
                content={"error": {"code": "NOT_READY", "message": "Database is unavailable"}},
            )

    register_exception_handlers(application)
    return application


def register_exception_handlers(application: FastAPI) -> None:
    @application.exception_handler(AppError)
    async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @application.exception_handler(RequestValidationError)
    async def validation_handler(_request: Request, exc: RequestValidationError) -> JSONResponse:
        message = "Invalid request"
        errors = exc.errors()
        if errors:
            loc = errors[0].get("loc", ())
            msg = errors[0].get("msg", message)
            field = loc[-1] if loc else "body"
            message = f"{field}: {msg}"
        return JSONResponse(
            status_code=422,
            content={"error": {"code": "VALIDATION_ERROR", "message": message}},
        )

    @application.exception_handler(StarletteHTTPException)
    async def http_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = "HTTP_ERROR"
        if exc.status_code == 401:
            code = "UNAUTHORIZED"
        elif exc.status_code == 403:
            code = "FORBIDDEN"
        elif exc.status_code == 404:
            code = "NOT_FOUND"
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": code, "message": str(exc.detail)}},
        )

    @application.exception_handler(Exception)
    async def unhandled_handler(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "error": {"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}
            },
        )


app = create_app()
