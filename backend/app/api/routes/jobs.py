"""Job streaming endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from ...services.jobs import JobManager
from ...services.runtime import job_manager

router = APIRouter()


def get_job_manager() -> JobManager:
    return job_manager


def get_job_repository():
    return job_manager.repository


@router.get("/{job_id}")
async def get_job(job_id: str, manager: JobManager = Depends(get_job_manager)):
    job = manager.repository.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/{job_id}/stream")
async def stream_job(job_id: str, manager: JobManager = Depends(get_job_manager)):
    async def event_generator():
        async for line in manager.stream(job_id):
            yield f"data: {line}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
