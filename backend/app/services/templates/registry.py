"""Template registry management."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from pydantic import BaseModel, Field

TEMPLATES_DIR = Path("templates")
REGISTRY_FILE = TEMPLATES_DIR / "registry.json"


class TemplateMetadata(BaseModel):
    identifier: str = Field(..., description="Unique template identifier")
    display_name: str
    license: str
    description: str | None = None
    engine: str = Field("pdflatex", description="Preferred LaTeX engine")
    citation_package: str = Field("natbib")
    assets_path: str = Field(..., description="Relative path to template root")


class TemplateRegistry:
    """Manage available templates and metadata."""

    def __init__(self, registry_file: Path | None = None) -> None:
        self.registry_file = registry_file or REGISTRY_FILE
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.registry_file.exists():
            self.registry_file.write_text(json.dumps({"templates": []}, indent=2), encoding="utf-8")

    def list_templates(self) -> List[TemplateMetadata]:
        data = json.loads(self.registry_file.read_text(encoding="utf-8"))
        return [TemplateMetadata(**item) for item in data.get("templates", [])]

    def get(self, identifier: str) -> TemplateMetadata | None:
        for template in self.list_templates():
            if template.identifier == identifier:
                return template
        return None

    def register(self, metadata: TemplateMetadata) -> TemplateMetadata:
        templates = self.list_templates()
        if any(t.identifier == metadata.identifier for t in templates):
            raise ValueError(f"Template {metadata.identifier} already registered")
        templates.append(metadata)
        self._write(templates)
        return metadata

    def _write(self, templates: Iterable[TemplateMetadata]) -> None:
        data = {"templates": [t.dict() for t in templates]}
        self.registry_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def resolve_path(self, identifier: str) -> Path:
        metadata = self.get(identifier)
        if not metadata:
            raise KeyError(identifier)
        return (TEMPLATES_DIR / metadata.assets_path).resolve()
