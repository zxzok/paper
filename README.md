# ManuWeaver

ManuWeaver is an end-to-end workflow for transforming Markdown manuscripts into journal-ready LaTeX packages with trustworthy references and compilation feedback. The platform orchestrates structural analysis using large language models, citation need detection, multi-source literature retrieval, bibliography normalization, LaTeX rendering, PDF compilation, and visual diffing for transparent author review.

## Features

- **Markdown ingestion & normalization** – Pandoc-based preprocessing with math harmonization and YAML front matter extraction.
- **Template aware layout** – Plugin registry with built-in `Generic-Article` and `IEEEtran` examples, plus external template import.
- **LLM-guided structuring** – Embedded prompts for section extraction, formatting advice, and citation audits (analysis prompt v1, citation_need_prompt v1, formatting_prompt v1).
- **Citation governance** – Rules + LLM detection of citation needs, followed by Crossref, OpenAlex, PubMed, and arXiv aggregation with DOI verification and BibTeX normalization.
- **Compilation automation** – Rendering through Jinja2 templates, Pandoc conversions, latexmk/Tectonic wrappers, and preflight QA with cross reference checks.
- **Review interface** – Next.js dashboard for project creation, streaming logs via SSE, citation decisions, LaTeX preview, preflight results, and artifact downloads.
- **Task orchestration** – FastAPI backend with Celery + Redis queue, SSE job streaming, and Dockerized deployment.

## Repository Layout

```
backend/   FastAPI app, Celery tasks, services, pipeline helpers
frontend/  Next.js 14 App Router UI with CodeMirror editor
infra/     Dockerfiles, docker-compose stack, TexLive installer, Makefile helpers
templates/ Template registry plus Generic-Article & IEEEtran assets
examples/  Sample manuscript and artifact descriptions
tests/     Pytest suites with VCR-ready backend tests and Playwright E2E skeleton
```

## Getting Started

### Prerequisites

- Docker and docker-compose (for containerized deployment)
- Python 3.11 with Poetry (for local backend development)
- Node.js 20+ with PNPM/NPM (for local frontend development)

### Environment Variables

Copy `.env.example` to `.env` and update values as needed:

```bash
cp .env.example .env
```

Key variables:

- `OPENAI_API_KEY` – LLM provider key (required for production inference).
- `CROSSREF_MAILTO`, `OPENALEX_BASE`, `NCBI_API_KEY`, `ARXIV_BASE` – API credentials/endpoints for reference retrieval.
- `REDIS_URL` – Celery broker/backend.
- `STORAGE_ROOT` – Persistent project storage directory.
- `ALLOWED_TEX_COMMANDS` – Whitelisted LaTeX commands after security filtering.
- `NEXT_PUBLIC_API_BASE` – Frontend-to-backend base URL.

### Docker Compose Deployment

One command brings up the entire stack (API, worker, frontend, Redis):

```bash
make compose-up
```

Once running, visit <http://localhost:3000> to access the UI. The API is served at <http://localhost:8000> with docs at `/docs`.

To stop and clean containers:

```bash
make compose-down
```

### Local Development (Backend)

```bash
poetry install
poetry run uvicorn backend.app.main:app --reload
```

Run Celery workers and Redis for background jobs:

```bash
redis-server --port 6379 &
poetry run celery -A backend.app.tasks.celery_app worker -l info
```

Execute backend tests:

```bash
poetry run pytest tests/backend
```

### Local Development (Frontend)

```bash
cd frontend
npm install
npm run dev
```

Playwright tests:

```bash
npm run test
```

## Usage Workflow

1. **Create Project** – Upload or paste Markdown, select a template, and submit. The backend stores the manuscript and initializes the project state.
2. **Format** – Run structural analysis to generate `normalized.json`, render `main.tex`, and inspect the LaTeX preview with diff metadata.
3. **Detect Citations** – Trigger the LLM + heuristic classifier to mark sentences that need citations. Review suggestions in the UI.
4. **Search References** – Aggregate literature from Crossref/OpenAlex/PubMed/arXiv. Candidates without verified DOI are flagged for manual review.
5. **Compile** – Build the LaTeX project with `latexmk` or Tectonic (template preference). Logs stream into the UI, and PDF artifacts are stored.
6. **Preflight** – Generate Markdown report summarizing reference counts, unresolved citations, missing assets, and template conformance.
7. **Export** – Download `main.tex`, `references.bib`, `changes.json`, `preflight.md`, and the compiled PDF from the artifacts panel.

## Template Management

Built-in templates live under `templates/` with metadata registered in `registry.json`. Each template includes:

- `main.tex.j2` – Jinja2 LaTeX skeleton with placeholders for normalized sections.
- Preferred citation package (`natbib` or `biblatex`).
- Engine hints for the LaTeX builder.

To import external templates, POST a ZIP archive to `/api/templates/import` with metadata fields. Uploaded assets are extracted within the template registry for later selection.

## Reference Integrity & Zero-Hallucination Policy

- References are **never** generated directly by the LLM.
- Every citation candidate must provide a DOI, PubMed ID, or equivalent authoritative identifier.
- Items missing identifiers are marked `needs_review` and highlighted in the UI.
- BibTeX keys are normalized to `{surname}{year}{firstword}` and deduplicated with DOI priority.
- Preflight checks ensure no unresolved citation keys remain before export.

## Security Hardening

- Uploaded manuscripts are sanitized (math normalization, escaping) before rendering.
- Template rendering enforces whitelisted LaTeX commands and disables `\write18`/shell-escape.
- Compilation runs inside isolated working directories with cleaning of intermediate files.
- API keys are sourced from environment variables—never commit secrets.

## Testing Strategy

- **Backend unit tests** (`tests/backend`) cover reference deduplication, BibTeX serialization, and pipeline assembly.
- **Integration test** ensures the sample manuscript renders main.tex and produces a preflight summary with DOI-backed references.
- **Frontend Playwright test** validates the wizard loads and is ready for project creation.
- Additional tests can capture API interactions via VCR to avoid hitting live services during CI.

Run all quality gates with:

```bash
make test
```

## Troubleshooting

| Issue | Resolution |
|-------|------------|
| Pandoc or latexmk missing | Ensure Docker image built via `make build` or install dependencies locally (`infra/install-texlive.sh`). |
| Citation search returns no DOI | Verify API keys/rate limits and inspect `needs_review` flags in the UI. |
| SSE stream disconnects | Confirm Redis and Celery workers are running; logs fall back to stored job history on reconnect. |
| Template compilation errors | Check `main.tex` for unsupported packages, review `Job Logs`, and adjust template metadata. |

## Academic Responsibility Statement

ManuWeaver accelerates citation discovery and manuscript formatting, but authors must independently verify every suggested reference, ensure ethical compliance, and validate the compiled PDF before submission. Automated suggestions should never replace domain expertise or due diligence.
