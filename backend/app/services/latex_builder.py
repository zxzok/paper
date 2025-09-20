"""LaTeX compilation helpers."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from ..models.core import CompileEngine


class LatexCompilationError(RuntimeError):
    pass


class LatexBuilder:
    def __init__(self, workdir: Path) -> None:
        self.workdir = workdir

    def compile(self, main_tex: Path, engine: CompileEngine, clean: bool = True) -> Path:
        if engine == CompileEngine.tectonic:
            return self._compile_with_tectonic(main_tex)
        return self._compile_with_latexmk(main_tex, engine)

    def _compile_with_latexmk(self, main_tex: Path, engine: CompileEngine) -> Path:
        command = [
            "latexmk",
            "-pdf" if engine != CompileEngine.tectonic else "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            str(main_tex.name),
        ]
        process = subprocess.run(command, cwd=self.workdir, capture_output=True)
        if process.returncode != 0:
            raise LatexCompilationError(process.stderr.decode("utf-8"))
        pdf_path = self.workdir / f"{main_tex.stem}.pdf"
        if not pdf_path.exists():
            raise LatexCompilationError("PDF not generated")
        return pdf_path

    def _compile_with_tectonic(self, main_tex: Path) -> Path:
        command = ["tectonic", str(main_tex.name)]
        process = subprocess.run(command, cwd=self.workdir, capture_output=True)
        if process.returncode != 0:
            raise LatexCompilationError(process.stderr.decode("utf-8"))
        pdf_path = self.workdir / f"{main_tex.stem}.pdf"
        if not pdf_path.exists():
            raise LatexCompilationError("PDF not generated")
        return pdf_path
