"""Security utilities for LaTeX compilation."""
from __future__ import annotations

import re
from typing import Iterable

from ..config import get_settings

FORBIDDEN_COMMANDS = {"\\write18", "\\input|/", "\\include|/"}


def is_safe_latex(content: str, allowed_commands: Iterable[str] | None = None) -> bool:
    settings = get_settings()
    allowed = set(cmd.strip() for cmd in (allowed_commands or settings.allowed_tex_commands.split(",")))
    for forbidden in FORBIDDEN_COMMANDS:
        if forbidden in content:
            return False
    pattern = re.compile(r"\\([a-zA-Z@]+)")
    for match in pattern.findall(content):
        cmd = f"\\{match}"
        if cmd not in allowed:
            continue
    return True
