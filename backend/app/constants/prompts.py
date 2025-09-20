"""Embedded prompt templates for ManuWeaver."""
from __future__ import annotations

analysis_prompt_v1 = """
You are ManuscriptStructurizer. Receive a Markdown manuscript between <md> tags. Produce a JSON object following these requirements:
- Preserve all scientific meaning, do not hallucinate facts.
- Organize content into explicit sections: title, authors, affiliations, abstract, keywords, introduction, methods, results, discussion, conclusion, acknowledgements, data_availability, conflict_of_interest, supplementary, appendix.
- Provide arrays for figures, tables, and equations, each with stable labels (e.g. fig:method-1).
- Include citation placeholders extracted from the text with their surrounding sentences.
- Return JSON matching the schema example:
{
  "title": str,
  "authors": [{"name": str, "affiliation": str | null}],
  "sections": [{"name": str, "content": str, "citations": [str]}],
  "figures": [{"label": str, "caption": str, "filename": str | null}],
  "tables": [{"label": str, "caption": str, "content": str}],
  "equations": [{"label": str, "latex": str}]
}
Wrap the JSON in triple backticks.
<md>
{markdown}
</md>
""".strip()


citation_need_prompt_v1 = """
You are CitationGuardian. For each sentence provided, decide whether a citation is required.
Return a JSON list where each element is:
{
  "sentence": str,
  "need_citation": bool,
  "reasons": [str],
  "query_terms": [str],
  "confidence": float between 0 and 1
}
Rules: Recommend citations when the sentence states quantitative claims, references external work, introduces datasets, or controversial statements. Never fabricate references.
Input:
{sentences}
""".strip()


formatting_prompt_v1 = """
You are TeXStylist. Analyze the structured manuscript data and provide formatting guidance.
Return JSON with keys: `line_spacing`, `math_environments`, `macro_suggestions`, `package_conflicts`, `unit_notes`, `diff`.
- Suggest inline vs display math usage and numbering strategy.
- Highlight any macros that require escaping or template specific adjustments.
- Diff should be a minimal textual description of suggested edits, not the full source.
Input JSON:
{structured_json}
""".strip()
