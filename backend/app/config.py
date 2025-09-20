"""Application configuration module."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Runtime configuration driven by environment variables."""

    environment: str = Field("development", description="Runtime environment name")
    storage_root: str = Field(
        "/workspace/paper/.manuweaver",
        description="Root directory for project storage",
        env="STORAGE_ROOT",
    )
    cors_allow_origins: List[str] = Field(default_factory=lambda: ["*"])
    redis_url: str = Field("redis://redis:6379/0", env="REDIS_URL")

    openai_api_key: str | None = Field(None, env="OPENAI_API_KEY")
    crossref_mailto: str | None = Field(None, env="CROSSREF_MAILTO")
    openalex_base: str = Field("https://api.openalex.org", env="OPENALEX_BASE")
    ncbi_api_key: str | None = Field(None, env="NCBI_API_KEY")
    arxiv_base: str = Field("http://export.arxiv.org/api", env="ARXIV_BASE")

    allowed_tex_commands: str = Field("\\usepackage,\\begin,\\end,\\cite,\\citep,\\citet,\\parencite,\\ref,\\label", env="ALLOWED_TEX_COMMANDS")
    texlive_profile: str | None = Field(None, env="TEXLIVE_PROFILE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()


def project_storage_root(settings: Settings | None = None) -> Path:
    settings = settings or get_settings()
    return Path(settings.storage_root)
