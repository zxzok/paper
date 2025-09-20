"""Health check endpoint."""
from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz", summary="Health check")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
