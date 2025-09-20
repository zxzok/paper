"""Job orchestration utilities with Server-Sent Events support."""
from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import AsyncGenerator, Awaitable, Callable

from ..models.core import CompileJob, JobStatus, PipelineStage
from .storage import JobRepository


class JobManager:
    def __init__(self, repository: JobRepository | None = None) -> None:
        self.repository = repository or JobRepository()
        self._queues: dict[str, asyncio.Queue[str]] = defaultdict(asyncio.Queue)

    async def stream(self, job_id: str) -> AsyncGenerator[str, None]:
        queue = self._queues[job_id]
        job = self.repository.get(job_id)
        if job:
            for line in job.logs:
                yield line
        while True:
            line = await queue.get()
            yield line
            if line == "__COMPLETE__":
                break

    async def run_task(
        self,
        project_id: str,
        stage: PipelineStage,
        handler: Callable[[CompileJob], Awaitable[dict | None]],
    ) -> CompileJob:
        job = self.repository.create(project_id=project_id, stage=stage)
        queue = self._queues[job.id]
        self.repository.mark_status(job.id, JobStatus.running)

        async def _runner() -> None:
            try:
                result = await handler(job)
                self.repository.mark_status(job.id, JobStatus.completed, result=result)
                queue.put_nowait("__COMPLETE__")
            except Exception as exc:  # pragma: no cover - defensive logging
                self.repository.mark_status(job.id, JobStatus.failed, error=str(exc))
                queue.put_nowait(f"ERROR: {exc}")
                queue.put_nowait("__COMPLETE__")

        asyncio.create_task(_runner())
        return job

    def emit(self, job_id: str, message: str) -> None:
        queue = self._queues[job_id]
        queue.put_nowait(message)
        self.repository.append_log(job_id, message)
