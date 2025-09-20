import httpx
import pytest

from backend.app.config import Settings
from backend.app.services.llm.client import LLMClient

respx = pytest.importorskip("respx")


@pytest.mark.asyncio
async def test_stub_provider_returns_none():
    settings = Settings(llm_provider="stub")
    client = LLMClient(settings=settings)
    result = await client.complete_json("not json")
    assert result is None


@pytest.mark.asyncio
@respx.mock
async def test_ollama_provider_parses_response(respx_mock):
    settings = Settings(llm_provider="ollama", ollama_base_url="http://ollama.test", ollama_model="llama3")
    respx_mock.post("http://ollama.test/api/generate").mock(
        return_value=httpx.Response(200, json={"response": "```json\\n{\\"foo\\": 1}\\n```"})
    )
    client = LLMClient(settings=settings)
    result = await client.complete_json("{}")
    assert result == {"foo": 1}


@pytest.mark.asyncio
@respx.mock
async def test_lmstudio_provider_parses_response(respx_mock):
    settings = Settings(llm_provider="lmstudio", lmstudio_base_url="http://lmstudio.test/v1", lmstudio_model="qwen")
    respx_mock.post("http://lmstudio.test/v1/chat/completions").mock(
        return_value=httpx.Response(200, json={"choices": [{"message": {"content": "{\"bar\": true}"}}]})
    )
    client = LLMClient(settings=settings)
    result = await client.complete_json("{}")
    assert result == {"bar": True}
