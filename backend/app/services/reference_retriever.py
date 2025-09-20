"""Unified reference retrieval across multiple providers."""
from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass
from typing import Iterable, List, Sequence, Callable

from rapidfuzz import fuzz

from ..models.core import Reference
from .reference.providers import DEFAULT_PROVIDERS, BaseProvider, ProviderResult

ProviderFactory = Callable[[], BaseProvider]


@dataclass
class RetrievalResult:
    references: List[Reference]


class ReferenceRetriever:
    def __init__(self, providers: Sequence[ProviderFactory] | None = None) -> None:
        self.providers: Sequence[ProviderFactory] = providers or [provider for provider in DEFAULT_PROVIDERS]

    async def search(self, query: str) -> RetrievalResult:
        tasks = [factory().search(query) for factory in self.providers]
        results: list[ProviderResult] = await asyncio.gather(*tasks, return_exceptions=False)
        merged = self._merge(results)
        return RetrievalResult(references=merged)

    def _merge(self, results: Iterable[ProviderResult]) -> List[Reference]:
        merged: dict[str, Reference] = {}
        for result in results:
            for record in result.records:
                key = self._make_key(record)
                similarity_key = next((k for k, ref in merged.items() if fuzz.ratio(ref.title.lower(), record.get("title", "").lower()) > 85), None)
                target_key = similarity_key or key
                existing = merged.get(target_key)
                reference = self._record_to_reference(record)
                if existing:
                    scores = [s for s in (existing.score, record.get("score")) if s is not None]
                    if scores:
                        existing.score = max(scores)
                    existing.source = ",".join(sorted(set(filter(None, [existing.source, record.get("source")]))))
                    if record.get("doi") and not existing.doi:
                        existing.doi = record.get("doi")
                    if record.get("url") and not existing.url:
                        existing.url = record.get("url")
                else:
                    merged[target_key] = reference
        return list(merged.values())

    @staticmethod
    def _make_key(record: dict) -> str:
        title = record.get("title", "")
        doi = record.get("doi")
        base = doi or title
        return hashlib.sha256(base.encode("utf-8")).hexdigest()

    @staticmethod
    def _record_to_reference(record: dict) -> Reference:
        title = record.get("title", "Untitled")
        authors = [a for a in record.get("authors", []) if a]
        year = record.get("year")
        doi = record.get("doi")
        url = record.get("url")
        key = ReferenceRetriever._canonical_key(title, authors, year)
        needs_review = doi is None
        return Reference(
            key=key,
            title=title,
            authors=authors,
            venue=record.get("venue"),
            year=year,
            doi=doi,
            url=url,
            source=record.get("source"),
            score=record.get("score"),
            needs_review=needs_review,
        )

    @staticmethod
    def _canonical_key(title: str, authors: list[str], year: int | None) -> str:
        primary = authors[0].split()[-1].lower() if authors else "anon"
        year_part = str(year) if year else "n.d."
        first_word = title.split()[0].lower() if title else "untitled"
        return f"{primary}{year_part}{first_word}"
