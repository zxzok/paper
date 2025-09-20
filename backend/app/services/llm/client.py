"""Minimal async LLM client wrapper."""
from __future__ import annotations

import asyncio
import json
from typing import Any, Dict


class LLMClient:
    """A placeholder LLM client that integrates with OpenAI compatible APIs."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()

    async def complete_json(self, prompt: str) -> Dict[str, Any] | None:
        # This stub simply returns None to trigger heuristic fallbacks in tests.
        # Integration hooks for actual LLMs can be added here.
        await asyncio.sleep(0)
        try:
            parsed = json.loads(prompt)
            if isinstance(parsed, dict) and "mock_response" in parsed:
                return parsed["mock_response"]
        except json.JSONDecodeError:
            pass
        return None
