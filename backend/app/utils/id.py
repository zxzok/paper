"""Identifier utilities."""
from __future__ import annotations

import secrets


def generate_id(prefix: str = "proj") -> str:
    return f"{prefix}_{secrets.token_hex(8)}"
