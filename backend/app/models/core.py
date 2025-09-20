"""Core Pydantic models used by the ManuWeaver backend."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Manuscript(BaseModel):
    content: str = Field(..., description="Raw Markdown manuscript content")
    filename: str | None = Field(None, description="Optional uploaded filename")


class TemplateSpec(BaseModel):
    identifier: str
    display_name: str
    license: str
    description: str | None = None
    engine: str = Field("pdflatex")
    citation_package: str = Field("natbib")
    assets_path: str = Field(..., description="Relative path to the template assets")


class CitationSlot(BaseModel):
    sentence: str
    need_citation: bool
    reasons: list[str]
    query_terms: list[str]
    confidence: float
    status: str = Field("pending", description="pending|confirmed|rejected|manual_review")


class Reference(BaseModel):
    key: str
    title: str
    authors: list[str]
    venue: str | None = None
    year: int | None = None
    doi: str | None = None
    url: str | None = None
    source: str | None = Field(None, description="Originating API provider")
    score: float | None = None
    needs_review: bool = False


class PipelineStage(str, Enum):
    import_stage = "import"
    structure = "structure"
    citation_detection = "citation_detection"
    reference_search = "reference_search"
    formatting = "formatting"
    compile = "compile"
    preflight = "preflight"


class ProjectStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    ready = "ready"
    failed = "failed"


class CompileEngine(str, Enum):
    latexmk = "latexmk"
    tectonic = "tectonic"


class Project(BaseModel):
    id: str
    manuscript: Manuscript
    template_id: str
    created_at: datetime
    status: ProjectStatus = ProjectStatus.pending
    normalized_json: Dict[str, Any] | None = None
    main_tex: str | None = None
    references: List[Reference] = Field(default_factory=list)
    citation_slots: List[CitationSlot] = Field(default_factory=list)
    pdf_path: str | None = None
    artifacts: Dict[str, str] = Field(default_factory=dict)


class CompileOptions(BaseModel):
    engine: CompileEngine = CompileEngine.latexmk
    font_engine: str | None = None
    clean_intermediate: bool = True


class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class CompileJob(BaseModel):
    id: str
    project_id: str
    stage: PipelineStage
    status: JobStatus = JobStatus.queued
    created_at: datetime
    updated_at: datetime
    logs: list[str] = Field(default_factory=list)
    result: dict[str, Any] | None = None
    error: str | None = None


class PreflightIssue(BaseModel):
    code: str
    severity: str
    message: str
    context: dict[str, Any] | None = None


class PreflightReport(BaseModel):
    project_id: str
    generated_at: datetime
    issues: list[PreflightIssue]
    summary: dict[str, Any] = Field(default_factory=dict)


class ProjectCreateRequest(BaseModel):
    template_id: str
    manuscript_text: str
    filename: str | None = None
    compile_options: CompileOptions | None = None


class ProjectCreateResponse(BaseModel):
    id: str
    status: ProjectStatus
    created_at: datetime


class CitationDetectionResponse(BaseModel):
    project_id: str
    slots: list[CitationSlot]
    job_id: str | None = None


class ReferenceSearchResponse(BaseModel):
    project_id: str
    references: list[Reference]
    job_id: str | None = None


class FormatResponse(BaseModel):
    project_id: str
    normalized_json: dict[str, Any]
    main_tex: str
    job_id: str | None = None


class CompileResponse(BaseModel):
    project_id: str
    pdf_path: str | None
    main_tex_path: str | None
    job_id: str | None = None


class PreflightResponse(BaseModel):
    project_id: str
    report: PreflightReport
    job_id: str | None = None


class ArtifactBundle(BaseModel):
    project_id: str
    files: dict[str, str]
