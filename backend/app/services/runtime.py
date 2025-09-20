"""Runtime singletons for shared services."""
from __future__ import annotations

from .jobs import JobManager
from .storage import JobRepository

job_manager = JobManager(JobRepository())

__all__ = ["job_manager"]
