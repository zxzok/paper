"""Apply confirmed citations into structured JSON."""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable, List

from ..models.core import CitationSlot, Reference


class CitationInserter:
    def apply(self, normalized: Dict[str, Any], citations: Iterable[CitationSlot], references: Iterable[Reference]) -> Dict[str, Any]:
        result = deepcopy(normalized)
        ref_map = {ref.key: ref for ref in references}
        slots = list(citations)
        for section in result.get("sections", []):
            content = section.get("content", "")
            for slot in slots:
                if slot.need_citation and slot.status == "confirmed":
                    key = slot.reasons[0] if slot.reasons else slot.sentence[:10]
                    ref = ref_map.get(key)
                    citation_cmd = f"\\citep{{{ref.key if ref else key}}}"
                    if slot.sentence in content:
                        content = content.replace(slot.sentence, f"{slot.sentence} {citation_cmd}")
            section["content"] = content
        return result
