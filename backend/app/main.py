"""FastAPI application entrypoint for ManuWeaver."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings, get_settings
from .api.routes import templates, projects, jobs, health

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = settings or get_settings()

    app = FastAPI(
        title="ManuWeaver API",
        version="0.1.0",
        description="Structured manuscript preparation and compilation service",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(templates.router, prefix="/api/templates", tags=["templates"])
    app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
    app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])

    @app.on_event("startup")
    async def _startup() -> None:  # pragma: no cover - simple logging hook
        logger.info("Starting ManuWeaver backend")
        Path(settings.storage_root).mkdir(parents=True, exist_ok=True)

    return app


app = create_app()
