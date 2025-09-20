"""Simple JSON-file based storage for projects and jobs."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable

from ..config import project_storage_root
from ..models.core import CompileJob, JobStatus, PipelineStage, Project
from ..utils.id import generate_id


class ProjectRepository:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or project_storage_root()
        self.root.mkdir(parents=True, exist_ok=True)

    def _project_path(self, project_id: str) -> Path:
        return self.root / f"{project_id}.json"

    def save(self, project: Project) -> Project:
        path = self._project_path(project.id)
        data = json.loads(project.json())
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        return project

    def get(self, project_id: str) -> Project | None:
        path = self._project_path(project_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return Project.parse_obj(data)

    def list_projects(self) -> Iterable[Project]:
        for path in self.root.glob("proj_*.json"):
            yield Project.parse_obj(json.loads(path.read_text(encoding="utf-8")))


class JobRepository:
    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or project_storage_root()) / "jobs"
        self.root.mkdir(parents=True, exist_ok=True)

    def _job_path(self, job_id: str) -> Path:
        return self.root / f"{job_id}.json"

    def create(self, project_id: str, stage: PipelineStage) -> CompileJob:
        job_id = generate_id("job")
        now = datetime.utcnow()
        job = CompileJob(
            id=job_id,
            project_id=project_id,
            stage=stage,
            status=JobStatus.queued,
            created_at=now,
            updated_at=now,
        )
        self.save(job)
        return job

    def save(self, job: CompileJob) -> CompileJob:
        data = json.loads(job.json())
        self._job_path(job.id).write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        return job

    def get(self, job_id: str) -> CompileJob | None:
        path = self._job_path(job_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return CompileJob.parse_obj(data)

    def append_log(self, job_id: str, message: str) -> None:
        job = self.get(job_id)
        if not job:
            raise KeyError(job_id)
        job.logs.append(message)
        job.updated_at = datetime.utcnow()
        self.save(job)

    def mark_status(self, job_id: str, status: JobStatus, error: str | None = None, result: Dict | None = None) -> CompileJob:
        job = self.get(job_id)
        if not job:
            raise KeyError(job_id)
        job.status = status
        job.updated_at = datetime.utcnow()
        if error:
            job.error = error
        if result is not None:
            job.result = result
        self.save(job)
        return job
