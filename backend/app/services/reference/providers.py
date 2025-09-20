"""Academic reference provider clients."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import httpx

from ...config import get_settings


@dataclass
class ProviderResult:
    source: str
    records: List[Dict[str, Any]]


class BaseProvider:
    name = "base"

    async def search(self, query: str) -> ProviderResult:
        raise NotImplementedError


class CrossrefProvider(BaseProvider):
    name = "crossref"

    async def search(self, query: str) -> ProviderResult:
        settings = get_settings()
        params = {"query": query, "rows": 5}
        if settings.crossref_mailto:
            params["mailto"] = settings.crossref_mailto
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://api.crossref.org/works", params=params)
            resp.raise_for_status()
            data = resp.json()
        records = []
        for item in data.get("message", {}).get("items", []):
            records.append(
                {
                    "title": item.get("title", [""])[0],
                    "authors": [" ".join([n for n in [a.get("given"), a.get("family")] if n]) for a in item.get("author", [])],
                    "year": item.get("issued", {}).get("date-parts", [[None]])[0][0],
                    "doi": item.get("DOI"),
                    "url": item.get("URL"),
                    "source": self.name,
                }
            )
        return ProviderResult(source=self.name, records=records)


class OpenAlexProvider(BaseProvider):
    name = "openalex"

    async def search(self, query: str) -> ProviderResult:
        settings = get_settings()
        params = {"search": query, "per-page": 5}
        async with httpx.AsyncClient(timeout=10, base_url=settings.openalex_base) as client:
            resp = await client.get("/works", params=params)
            resp.raise_for_status()
            data = resp.json()
        records = []
        for item in data.get("results", []):
            records.append(
                {
                    "title": item.get("title"),
                    "authors": [auth.get("author", {}).get("display_name") for auth in item.get("authorships", [])],
                    "year": item.get("publication_year"),
                    "doi": item.get("doi"),
                    "url": item.get("id"),
                    "source": self.name,
                }
            )
        return ProviderResult(source=self.name, records=records)


class PubMedProvider(BaseProvider):
    name = "pubmed"

    async def search(self, query: str) -> ProviderResult:
        params = {"db": "pubmed", "term": query, "retmode": "json", "retmax": 5}
        async with httpx.AsyncClient(timeout=10, base_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils") as client:
            ids_resp = await client.get("/esearch.fcgi", params=params)
            ids_resp.raise_for_status()
            ids = ids_resp.json().get("esearchresult", {}).get("idlist", [])
            records: list[dict[str, Any]] = []
            if ids:
                summary_resp = await client.get("/esummary.fcgi", params={"db": "pubmed", "id": ",".join(ids), "retmode": "json"})
                summary_resp.raise_for_status()
                data = summary_resp.json().get("result", {})
                for identifier in ids:
                    item = data.get(identifier, {})
                    records.append(
                        {
                            "title": item.get("title"),
                            "authors": [a.get("name") for a in item.get("authors", [])],
                            "year": int(item.get("pubdate", "0")[:4]) if item.get("pubdate") else None,
                            "doi": item.get("elocationid"),
                            "url": f"https://pubmed.ncbi.nlm.nih.gov/{identifier}/",
                            "source": self.name,
                        }
                    )
        return ProviderResult(source=self.name, records=records)


class ArxivProvider(BaseProvider):
    name = "arxiv"

    async def search(self, query: str) -> ProviderResult:
        params = {"search_query": query, "start": 0, "max_results": 5}
        async with httpx.AsyncClient(timeout=10, base_url="http://export.arxiv.org/api") as client:
            resp = await client.get("/query", params=params)
            resp.raise_for_status()
            text = resp.text
        records = []
        for entry in text.split("<entry>")[1:]:
            title = entry.split("<title>")[1].split("</title>")[0].strip()
            records.append(
                {
                    "title": title,
                    "authors": [],
                    "year": None,
                    "doi": None,
                    "url": None,
                    "source": self.name,
                }
            )
        return ProviderResult(source=self.name, records=records)


DEFAULT_PROVIDERS: list[type[BaseProvider]] = [
    CrossrefProvider,
    OpenAlexProvider,
    PubMedProvider,
    ArxivProvider,
]
