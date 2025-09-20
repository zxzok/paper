"""Preflight report generation."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from ..models.core import PreflightIssue, PreflightReport, Project


class PreflightGenerator:
    def run(self, project: Project) -> PreflightReport:
        issues: List[PreflightIssue] = []
        if not project.references:
            issues.append(
                PreflightIssue(
                    code="missing_references",
                    severity="warning",
                    message="No references have been confirmed",
                    context={},
                )
            )
        if project.main_tex and "\\cite" in project.main_tex and not project.references:
            issues.append(
                PreflightIssue(
                    code="orphan_citations",
                    severity="error",
                    message="Citations present but references.bib empty",
                    context={},
                )
            )
        summary = {
            "sections": len(project.normalized_json.get("sections", [])) if project.normalized_json else 0,
            "references": len(project.references),
        }
        return PreflightReport(
            project_id=project.id,
            generated_at=datetime.utcnow(),
            issues=issues,
            summary=summary,
        )

    def to_markdown(self, report: PreflightReport) -> str:
        lines = [f"# Preflight Report for {report.project_id}", "", "## Summary"]
        for key, value in report.summary.items():
            lines.append(f"- {key}: {value}")
        if report.issues:
            lines.append("\n## Issues")
            for issue in report.issues:
                lines.append(f"- **{issue.severity.upper()}** [{issue.code}] {issue.message}")
        else:
            lines.append("\nNo blocking issues detected.")
        return "\n".join(lines)
