"""Manuscript ingestion and preprocessing."""
from __future__ import annotations

import re
from dataclasses import dataclass

from ..models.core import Manuscript

INLINE_MATH_PATTERN = re.compile(r"\$(.+?)\$")
DISPLAY_MATH_PATTERN = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)


@dataclass
class IngestResult:
    manuscript: Manuscript
    cleaned_markdown: str


def normalize_equations(markdown: str) -> str:
    """Normalize inline and display math markers."""

    def _inline(match: re.Match[str]) -> str:
        return f"\\({match.group(1).strip()}\\)"

    def _display(match: re.Match[str]) -> str:
        return f"\\[{match.group(1).strip()}\\]"

    markdown = DISPLAY_MATH_PATTERN.sub(_display, markdown)
    markdown = INLINE_MATH_PATTERN.sub(_inline, markdown)
    return markdown


def sanitize_markdown(markdown: str) -> str:
    markdown = normalize_equations(markdown)
    markdown = markdown.replace("\r\n", "\n").strip()
    return markdown


def ingest_manuscript(manuscript: Manuscript) -> IngestResult:
    cleaned = sanitize_markdown(manuscript.content)
    return IngestResult(manuscript=manuscript, cleaned_markdown=cleaned)
