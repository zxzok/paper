"""Citation need detection service."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import List

from .llm.client import LLMClient
from ..constants.prompts import citation_need_prompt_v1
from ..models.core import CitationSlot

@dataclass
class CitationDetectionResult:
    slots: List[CitationSlot]


class CitationDetector:
    def __init__(self, client: LLMClient | None = None) -> None:
        self.client = client or LLMClient()

    @staticmethod
    def _split_sentences(text: str) -> List[str]:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return [s for s in sentences if s]

    async def detect(self, text: str) -> CitationDetectionResult:
        sentences = self._split_sentences(text)
        payload = citation_need_prompt_v1.format(sentences=json.dumps(sentences, ensure_ascii=False))
        response = await self.client.complete_json(payload)
        slots: List[CitationSlot] = []
        if isinstance(response, list):
            for item in response:
                slots.append(CitationSlot(**item))
        else:
            for sentence in sentences:
                need = any(keyword in sentence.lower() for keyword in ["study", "dataset", "we propose", "%"])
                slots.append(
                    CitationSlot(
                        sentence=sentence,
                        need_citation=need,
                        reasons=["heuristic keyword match"] if need else ["general statement"],
                        query_terms=sentence.split()[:5],
                        confidence=0.4 if need else 0.2,
                        status="pending",
                    )
                )
        return CitationDetectionResult(slots=slots)
