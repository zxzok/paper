"""BibTeX management utilities."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List

from ..models.core import Reference


@dataclass
class BibDatabase:
    entries: List[Reference]


class BibManager:
    def __init__(self) -> None:
        self._key_pattern = re.compile(r"[^a-zA-Z0-9]+");

    def normalize_key(self, reference: Reference) -> str:
        key = reference.key
        key = self._key_pattern.sub("", key)
        return key

    def deduplicate(self, references: Iterable[Reference]) -> BibDatabase:
        seen: dict[str, Reference] = {}
        for ref in references:
            key = self.normalize_key(ref)
            if key not in seen:
                seen[key] = ref
            else:
                existing = seen[key]
                if ref.doi and not existing.doi:
                    existing.doi = ref.doi
                if ref.url and not existing.url:
                    existing.url = ref.url
                existing.needs_review = existing.needs_review or ref.needs_review
        return BibDatabase(entries=list(seen.values()))

    def to_bibtex(self, db: BibDatabase) -> str:
        chunks = []
        for ref in db.entries:
            chunks.append(self._entry_to_bibtex(ref))
        return "\n\n".join(chunks)

    def _entry_to_bibtex(self, reference: Reference) -> str:
        fields = {
            "title": reference.title,
            "author": " and ".join(reference.authors),
            "year": reference.year,
            "journal": reference.venue,
            "doi": reference.doi,
            "url": reference.url,
        }
        formatted_fields = [f"  {key} = {{{value}}}" for key, value in fields.items() if value]
        return "@article{{{key},\n{fields}\n}}".format(key=self.normalize_key(reference), fields=",\n".join(formatted_fields))
