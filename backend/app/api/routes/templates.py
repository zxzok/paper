"""Template management endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from ...models.core import TemplateSpec
from ...services.templates import TemplateRegistry
from ...services.templates.registry import TemplateMetadata

router = APIRouter()


def get_registry() -> TemplateRegistry:
    return TemplateRegistry()


@router.get("/", response_model=list[TemplateSpec])
async def list_templates(registry: TemplateRegistry = Depends(get_registry)) -> list[TemplateSpec]:
    return [TemplateSpec(**t.dict()) for t in registry.list_templates()]


@router.get("/{identifier}", response_model=TemplateSpec)
async def get_template(identifier: str, registry: TemplateRegistry = Depends(get_registry)) -> TemplateSpec:
    template = registry.get(identifier)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return TemplateSpec(**template.dict())


@router.post("/import", response_model=TemplateSpec)
async def import_template(
    identifier: str = Form(...),
    display_name: str = Form(...),
    license: str = Form(...),
    description: str | None = Form(None),
    engine: str = Form("pdflatex"),
    citation_package: str = Form("natbib"),
    archive: UploadFile | None = File(None),
    registry: TemplateRegistry = Depends(get_registry),
) -> TemplateSpec:
    # For brevity we only register metadata and expect manual extraction of assets when archive provided.
    metadata = registry.register(
        TemplateMetadata(
            identifier=identifier,
            display_name=display_name,
            license=license,
            description=description,
            engine=engine,
            citation_package=citation_package,
            assets_path=identifier,
        )
    )
    return TemplateSpec(**metadata.dict())
