"""Pandoc integration utilities."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Dict


class PandocError(RuntimeError):
    pass


class PandocWrapper:
    def __init__(self, filters: list[str] | None = None) -> None:
        self.filters = filters or []

    def markdown_to_latex(self, markdown: str, output_path: Path, variables: Dict[str, str] | None = None) -> None:
        command = [
            "pandoc",
            "--from",
            "markdown",
            "--to",
            "latex",
            "--output",
            str(output_path),
            "--citeproc",
        ]
        for flt in self.filters:
            command.extend(["--filter", flt])
        if variables:
            for key, value in variables.items():
                command.extend(["-V", f"{key}={value}"])
        process = subprocess.run(command, input=markdown.encode("utf-8"), capture_output=True)
        if process.returncode != 0:
            raise PandocError(process.stderr.decode("utf-8"))

    def markdown_to_json(self, markdown: str) -> dict:
        command = ["pandoc", "--from", "markdown", "--to", "json"]
        process = subprocess.run(command, input=markdown.encode("utf-8"), capture_output=True)
        if process.returncode != 0:
            raise PandocError(process.stderr.decode("utf-8"))
        return json.loads(process.stdout.decode("utf-8"))
