import json
from datetime import datetime

import pytest

from backend.app.models.core import Manuscript, Project
from backend.app.services.renderer import render_main_tex
from backend.app.services.structure_analyzer import StructureAnalyzer
from backend.app.services.preflight import PreflightGenerator
from backend.app.services.storage import ProjectRepository
from backend.app.services.reference_retriever import ReferenceRetriever
from backend.app.services.reference.providers import BaseProvider, ProviderResult
from backend.app.services.bib_manager import BibManager
from backend.app.utils.id import generate_id


class StaticProvider(BaseProvider):
    name = "static"

    async def search(self, query: str):
        return ProviderResult(
            source=self.name,
            records=[
                {
                    "title": "Open Science Dataset",
                    "authors": ["Maria Curie"],
                    "year": 2020,
                    "doi": "10.1000/osd",
                    "url": "https://doi.org/10.1000/osd",
                    "source": self.name,
                }
            ],
        )


@pytest.mark.asyncio
async def test_pipeline_generates_artifacts(tmp_path, monkeypatch):
    project_id = generate_id()
    manuscript = Manuscript(content="# Title\n\nWe evaluate a dataset with 95% accuracy.")
    project = Project(
        id=project_id,
        manuscript=manuscript,
        template_id="Generic-Article",
        created_at=datetime.utcnow(),
    )
    repo = ProjectRepository()
    repo.save(project)

    analyzer = StructureAnalyzer()
    structure = await analyzer.analyze(manuscript.content)
    project.normalized_json = structure.normalized
    project.main_tex = render_main_tex(structure.normalized, project.template_id)

    retriever = ReferenceRetriever(providers=[StaticProvider])
    refs = await retriever.search("dataset accuracy")
    bib_manager = BibManager()
    bib_db = bib_manager.deduplicate(refs.references)
    project.references = bib_db.entries

    generator = PreflightGenerator()
    report = generator.run(project)
    assert report.summary["references"] == 1
    assert "documentclass" in project.main_tex
