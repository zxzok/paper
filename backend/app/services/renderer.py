"""Render normalized manuscript into LaTeX using templates."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .templates.registry import TemplateRegistry


def render_main_tex(normalized: Dict[str, Any], template_id: str) -> str:
    registry = TemplateRegistry()
    metadata = registry.get(template_id)
    if not metadata:
        raise ValueError(f"Template {template_id} not found")
    template_root = (Path("templates") / metadata.assets_path)
    env = Environment(loader=FileSystemLoader(template_root), autoescape=select_autoescape([]))
    template = env.get_template("main.tex.j2")
    return template.render(doc=normalized, template=metadata.dict())
