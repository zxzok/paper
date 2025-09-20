"""Application configuration module."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from pydantic import BaseModel, Field

_ENV_VAR_MAP: Dict[str, str] = {
    "storage_root": "STORAGE_ROOT",
    "redis_url": "REDIS_URL",
    "openai_api_key": "OPENAI_API_KEY",
    "crossref_mailto": "CROSSREF_MAILTO",
    "openalex_base": "OPENALEX_BASE",
    "ncbi_api_key": "NCBI_API_KEY",
    "arxiv_base": "ARXIV_BASE",
    "allowed_tex_commands": "ALLOWED_TEX_COMMANDS",
    "texlive_profile": "TEXLIVE_PROFILE",
}

load_dotenv()


class Settings(BaseModel):
    """Runtime configuration driven by environment variables."""

    environment: str = Field("development", description="Runtime environment name")
    storage_root: str = Field(
        "/workspace/paper/.manuweaver",
        description="Root directory for project storage",
    )
    cors_allow_origins: List[str] = Field(default_factory=lambda: ["*"])
    redis_url: str = Field("redis://redis:6379/0")

    openai_api_key: str | None = None
    crossref_mailto: str | None = None
    openalex_base: str = Field("https://api.openalex.org")
    ncbi_api_key: str | None = None
    arxiv_base: str = Field("http://export.arxiv.org/api")

    allowed_tex_commands: str = Field(
        "\\usepackage,\\begin,\\end,\\cite,\\citep,\\citet,\\parencite,\\ref,\\label"
    )
    texlive_profile: str | None = None

    @classmethod
    def from_env(cls) -> "Settings":
        """Create settings by loading overrides from environment variables."""

        overrides: Dict[str, Any] = {}
        for field_name, env_name in _ENV_VAR_MAP.items():
            value = os.environ.get(env_name)
            if value is None:
                continue
            overrides[field_name] = value

        return cls(**overrides)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings.from_env()


def project_storage_root(settings: Settings | None = None) -> Path:
    settings = settings or get_settings()
    return Path(settings.storage_root)
