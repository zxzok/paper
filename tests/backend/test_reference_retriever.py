import pytest

from backend.app.models.core import Reference
from backend.app.services.reference.providers import ProviderResult, BaseProvider
from backend.app.services.reference_retriever import ReferenceRetriever


class StubProvider(BaseProvider):
    name = "stub"

    def __init__(self, payload):
        self.payload = payload

    async def search(self, query: str):  # pragma: no cover - direct invocation
        return ProviderResult(source=self.name, records=self.payload)


@pytest.mark.asyncio
async def test_reference_retriever_deduplicates():
    payload_a = [
        {
            "title": "Sample Research",
            "authors": ["Alice Smith"],
            "year": 2021,
            "doi": "10.1000/sample",
            "url": "https://doi.org/10.1000/sample",
            "source": "crossref",
        }
    ]
    payload_b = [
        {
            "title": "Sample Research",
            "authors": ["A. Smith"],
            "year": 2021,
            "doi": "10.1000/sample",
            "url": "https://doi.org/10.1000/sample",
            "source": "openalex",
        }
    ]
    retriever = ReferenceRetriever(providers=[lambda: StubProvider(payload_a), lambda: StubProvider(payload_b)])
    result = await retriever.search("sample")
    assert len(result.references) == 1
    ref = result.references[0]
    assert ref.doi == "10.1000/sample"
    assert "crossref" in ref.source
    assert "openalex" in ref.source
