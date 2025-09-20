
"""Minimal async LLM client wrapper with local provider support."""

from __future__ import annotations

import asyncio
import json

import re
from typing import Any, Dict

import httpx

from ...config import Settings, get_settings


class LLMClient:
    """LLM client supporting stub, Ollama, and LM Studio backends."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._lock = asyncio.Lock()
        self.settings = settings or get_settings()

    async def complete_json(self, prompt: str) -> Dict[str, Any] | None:
        provider = (self.settings.llm_provider or "stub").lower()
        async with self._lock:
            if provider == "ollama":
                text = await self._call_ollama(prompt)
                return self._parse_json_output(text)
            if provider == "lmstudio":
                text = await self._call_lmstudio(prompt)
                return self._parse_json_output(text)
            return self._parse_stub(prompt)

    async def _call_ollama(self, prompt: str) -> str:
        url = f"{self.settings.ollama_base_url.rstrip('/')}/api/generate"
        payload = {
            "model": self.settings.ollama_model,
            "prompt": prompt,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
        return data.get("response", "")

    async def _call_lmstudio(self, prompt: str) -> str:
        url = f"{self.settings.lmstudio_base_url.rstrip('/')}/chat/completions"
        payload = {
            "model": self.settings.lmstudio_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
        choices = data.get("choices", [])
        if not choices:
            return ""
        message = choices[0].get("message", {})
        return message.get("content", "")

    @staticmethod
    def _parse_json_output(text: str) -> Dict[str, Any] | None:
        if not text:
            return None
        cleaned = text.strip()
        fences = re.findall(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.DOTALL)
        candidates = fences if fences else [cleaned]
        for candidate in candidates:
            candidate = candidate.strip()
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue
        return None

    @staticmethod
    def _parse_stub(prompt: str) -> Dict[str, Any] | None:

        try:
            parsed = json.loads(prompt)
            if isinstance(parsed, dict) and "mock_response" in parsed:
                return parsed["mock_response"]
        except json.JSONDecodeError:
            pass
        return None
