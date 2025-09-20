"""Structure analysis using LLM prompts with deterministic fallback."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .llm.client import LLMClient
from ..constants.prompts import analysis_prompt_v1


@dataclass
class StructureResult:
    normalized: Dict[str, Any]


class StructureAnalyzer:
    def __init__(self, client: LLMClient | None = None) -> None:
        self.client = client or LLMClient()

    async def analyze(self, markdown: str) -> StructureResult:
        payload = analysis_prompt_v1.replace("{markdown}", markdown)
        response = await self.client.complete_json(payload)
        if response:
            return StructureResult(normalized=response)
        # fallback minimal structure
        return StructureResult(
            normalized={
                "title": "Untitled Manuscript",
                "sections": [
                    {"name": "Body", "content": markdown, "citations": []},
                ],
                "figures": [],
                "tables": [],
            }
        )
