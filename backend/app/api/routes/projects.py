"""Project orchestration endpoints."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Body

from ...config import project_storage_root
from ...models.core import (
    ArtifactBundle,
    CitationDetectionResponse,
    CompileOptions,
    CompileResponse,
    FormatResponse,
    PipelineStage,
    PreflightResponse,
    Project,
    ProjectCreateRequest,
    ProjectCreateResponse,
    ProjectStatus,
    ReferenceSearchResponse,
    Manuscript,
)
from ...services.bib_manager import BibManager
from ...services.citation_detector import CitationDetector
from ...services.diff_engine import DiffEngine
from ...services.ingest import ingest_manuscript
from ...services.latex_builder import LatexBuilder, LatexCompilationError
from ...services.preflight import PreflightGenerator
from ...services.reference_retriever import ReferenceRetriever
from ...services.renderer import render_main_tex
from ...services.runtime import job_manager
from ...services.storage import ProjectRepository
from ...services.structure_analyzer import StructureAnalyzer
from ...utils.id import generate_id
from ...security import is_safe_latex

router = APIRouter()


def get_repo() -> ProjectRepository:
    return ProjectRepository()


async def get_project(project_id: str, repo: ProjectRepository) -> Project:
    project = repo.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", response_model=ProjectCreateResponse)
async def create_project(request: ProjectCreateRequest, repo: ProjectRepository = Depends(get_repo)) -> ProjectCreateResponse:
    project_id = generate_id()
    manuscript = Manuscript(content=request.manuscript_text, filename=request.filename)
    ingest_result = ingest_manuscript(manuscript)
    project = Project(
        id=project_id,
        manuscript=manuscript,
        template_id=request.template_id,
        created_at=datetime.utcnow(),
        status=ProjectStatus.pending,
    )
    repo.save(project)
    project_dir = project_storage_root() / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "manuscript.md").write_text(ingest_result.cleaned_markdown, encoding="utf-8")
    return ProjectCreateResponse(id=project_id, status=project.status, created_at=project.created_at)


@router.post("/{project_id}/detect-citations", response_model=CitationDetectionResponse)
async def detect_citations(project_id: str, repo: ProjectRepository = Depends(get_repo)) -> CitationDetectionResponse:
    project = await get_project(project_id, repo)

    async def handler(job):
        detector = CitationDetector()
        job_manager.emit(job.id, "Starting citation detection")
        result = await detector.detect(project.manuscript.content)
        project.citation_slots = result.slots
        repo.save(project)
        job_manager.emit(job.id, f"Detected {len(result.slots)} candidate citations")
        return {"slots": [slot.dict() for slot in result.slots]}

    job = await job_manager.run_task(project_id, PipelineStage.citation_detection, handler)
    return CitationDetectionResponse(project_id=project_id, slots=project.citation_slots, job_id=job.id)


@router.post("/{project_id}/search-refs", response_model=ReferenceSearchResponse)
async def search_references(project_id: str, repo: ProjectRepository = Depends(get_repo)) -> ReferenceSearchResponse:
    project = await get_project(project_id, repo)

    async def handler(job):
        retriever = ReferenceRetriever()
        query = project.normalized_json.get("title") if project.normalized_json else project.manuscript.content.split("\n", 1)[0]
        job_manager.emit(job.id, f"Searching references with query: {query[:80]}")
        result = await retriever.search(query)
        bib_manager = BibManager()
        bib_db = bib_manager.deduplicate(result.references)
        project.references = bib_db.entries
        project_dir = project_storage_root() / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        references_path = project_dir / "references.bib"
        references_path.write_text(bib_manager.to_bibtex(bib_db), encoding="utf-8")
        project.artifacts["references"] = str(references_path)
        repo.save(project)
        job_manager.emit(job.id, f"Aggregated {len(project.references)} references")
        return {"references": [ref.dict() for ref in project.references]}

    job = await job_manager.run_task(project_id, PipelineStage.reference_search, handler)
    return ReferenceSearchResponse(project_id=project_id, references=project.references, job_id=job.id)


@router.post("/{project_id}/format", response_model=FormatResponse)
async def format_project(project_id: str, repo: ProjectRepository = Depends(get_repo)) -> FormatResponse:
    project = await get_project(project_id, repo)
    analyzer = StructureAnalyzer()
    result = await analyzer.analyze(project.manuscript.content)
    normalized = result.normalized
    main_tex = render_main_tex(normalized, project.template_id)
    project.normalized_json = normalized
    project.main_tex = main_tex
    project.status = ProjectStatus.processing
    repo.save(project)
    project_dir = project_storage_root() / project_id
    (project_dir / "normalized.json").write_text(json.dumps(normalized, indent=2), encoding="utf-8")
    (project_dir / "main.tex").write_text(main_tex, encoding="utf-8")
    diff_engine = DiffEngine()
    diff = diff_engine.compare(project.manuscript.content, main_tex)
    (project_dir / "changes.json").write_text(diff_engine.to_json(diff), encoding="utf-8")
    project.artifacts["changes"] = str(project_dir / "changes.json")
    repo.save(project)
    return FormatResponse(project_id=project_id, normalized_json=normalized, main_tex=main_tex)


@router.post("/{project_id}/compile", response_model=CompileResponse)
async def compile_project(
    project_id: str,
    options: CompileOptions | None = Body(None),
    repo: ProjectRepository = Depends(get_repo),
) -> CompileResponse:
    project = await get_project(project_id, repo)
    if not project.main_tex:
        raise HTTPException(status_code=400, detail="Project not formatted yet")
    if not is_safe_latex(project.main_tex):
        raise HTTPException(status_code=400, detail="Unsafe LaTeX content detected")
    project_dir = project_storage_root() / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    main_tex_path = project_dir / "main.tex"
    main_tex_path.write_text(project.main_tex, encoding="utf-8")
    builder = LatexBuilder(project_dir)
    engine = options.engine if options else CompileOptions().engine
    try:
        pdf_path = builder.compile(main_tex_path, engine)
    except LatexCompilationError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    project.pdf_path = str(pdf_path)
    project.artifacts.update({"pdf": str(pdf_path), "main_tex": str(main_tex_path)})
    project.status = ProjectStatus.ready
    repo.save(project)
    return CompileResponse(project_id=project_id, pdf_path=str(pdf_path), main_tex_path=str(main_tex_path))


@router.post("/{project_id}/preflight", response_model=PreflightResponse)
async def preflight(project_id: str, repo: ProjectRepository = Depends(get_repo)) -> PreflightResponse:
    project = await get_project(project_id, repo)
    generator = PreflightGenerator()
    report = generator.run(project)
    project_dir = project_storage_root() / project_id
    (project_dir / "preflight.md").write_text(generator.to_markdown(report), encoding="utf-8")
    project.artifacts["preflight"] = str(project_dir / "preflight.md")
    repo.save(project)
    return PreflightResponse(project_id=project_id, report=report)


@router.get("/{project_id}/artifacts", response_model=ArtifactBundle)
async def get_artifacts(project_id: str, repo: ProjectRepository = Depends(get_repo)) -> ArtifactBundle:
    project = await get_project(project_id, repo)
    return ArtifactBundle(project_id=project_id, files=project.artifacts)
