"""Celery tasks for the manuscript pipeline."""
from __future__ import annotations

import asyncio

from .celery_app import celery_app
from ..services.citation_detector import CitationDetector
from ..services.reference_retriever import ReferenceRetriever
from ..services.storage import ProjectRepository


@celery_app.task(name="pipeline.detect_citations")
def detect_citations_task(project_id: str) -> dict:
    repo = ProjectRepository()
    project = repo.get(project_id)
    if not project:
        raise ValueError("Project not found")
    detector = CitationDetector()
    result = asyncio.run(detector.detect(project.manuscript.content))
    project.citation_slots = result.slots
    repo.save(project)
    return {"count": len(result.slots)}


@celery_app.task(name="pipeline.search_references")
def search_references_task(project_id: str, query: str) -> dict:
    repo = ProjectRepository()
    project = repo.get(project_id)
    if not project:
        raise ValueError("Project not found")
    retriever = ReferenceRetriever()
    result = asyncio.run(retriever.search(query))
    project.references = result.references
    repo.save(project)
    return {"count": len(result.references)}
