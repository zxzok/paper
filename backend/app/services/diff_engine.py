"""Compute manuscript diffs."""
from __future__ import annotations

import json
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import List


@dataclass
class DiffResult:
    changes: List[dict]


class DiffEngine:
    def compare(self, original: str, formatted: str) -> DiffResult:
        matcher = SequenceMatcher(a=original.splitlines(), b=formatted.splitlines())
        changes: list[dict] = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            changes.append(
                {
                    "tag": tag,
                    "original": "\n".join(original.splitlines()[i1:i2]),
                    "formatted": "\n".join(formatted.splitlines()[j1:j2]),
                }
            )
        return DiffResult(changes=changes)

    def to_json(self, result: DiffResult) -> str:
        return json.dumps({"changes": result.changes}, indent=2)
