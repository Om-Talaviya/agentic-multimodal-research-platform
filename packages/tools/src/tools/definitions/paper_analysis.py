"""Tools for academic paper structure extraction, section queries, and cross-paper methodology comparisons."""

from typing import Any, Dict, List, Optional
from tools.base import BaseTool, ToolResult
from shared.logging import get_logger

logger = get_logger(__name__)


class PaperAnalysisTool(BaseTool):
    """Tool for analyzing academic paper structures, extracting dimensions, and querying sections."""

    @property
    def name(self) -> str:
        return "paper_analysis"

    @property
    def description(self) -> str:
        return (
            "Analyzes structured academic papers, preprints, and research manuscripts. "
            "Extracts key dimensions (Objective, Proposed Architecture, Baselines, Benchmarks, "
            "Metric Results, Limitations) or retrieves specific structural sections."
        )

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["extract_structure", "query_section", "extract_benchmarks"],
                    "description": "Operation to perform on the paper.",
                },
                "paper_structure": {
                    "type": "object",
                    "description": "Parsed PaperStructure dictionary or object.",
                },
                "paper_text": {
                    "type": "string",
                    "description": "Raw markdown or text of the academic paper.",
                },
                "section_type": {
                    "type": "string",
                    "description": "Target section type (e.g. 'methodology', 'results', 'limitations') for query_section.",
                },
            },
            "required": ["operation"],
        }

    async def execute(self, **kwargs: Any) -> ToolResult:
        operation = kwargs.get("operation")
        paper_struct = kwargs.get("paper_structure") or {}
        paper_text = kwargs.get("paper_text") or ""
        section_type = kwargs.get("section_type")

        try:
            if operation == "extract_structure":
                return self._extract_structure(paper_struct, paper_text)
            elif operation == "query_section":
                if not section_type:
                    return ToolResult(success=False, error="section_type parameter is required for query_section")
                return self._query_section(paper_struct, paper_text, section_type)
            elif operation == "extract_benchmarks":
                return self._extract_benchmarks(paper_struct, paper_text)
            else:
                return ToolResult(success=False, error=f"Unknown paper analysis operation: {operation}")
        except Exception as e:
            logger.error("PaperAnalysisTool execution failed", operation=operation, error=str(e))
            return ToolResult(success=False, error=f"PaperAnalysis error: {str(e)}")

    def _extract_structure(self, paper_struct: Dict[str, Any], raw_text: str) -> ToolResult:
        title = paper_struct.get("title", "")
        authors = paper_struct.get("authors", [])
        abstract = paper_struct.get("abstract", "")
        sections = paper_struct.get("sections", [])
        methodology = paper_struct.get("methodology_summary", "")
        limitations = paper_struct.get("limitations_summary", "")

        # If sections list not in struct, infer from raw text
        if not sections and raw_text:
            lines = raw_text.split("\n")
            title = title or (lines[0] if lines else "Research Paper")

        res_data = {
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "section_count": len(sections),
            "section_titles": [s.get("title") for s in sections if isinstance(s, dict)],
            "methodology_summary": methodology,
            "limitations_summary": limitations,
            "has_limitations": bool(limitations),
            "reference_count": len(paper_struct.get("bibliography", [])),
        }

        return ToolResult(success=True, data=res_data)

    def _query_section(self, paper_struct: Dict[str, Any], raw_text: str, target_type: str) -> ToolResult:
        sections = paper_struct.get("sections", [])
        matched = []

        target_lower = target_type.lower()
        for s in sections:
            s_type = s.get("section_type", "").lower() if isinstance(s, dict) else getattr(s, "section_type", "").lower()
            s_title = s.get("title", "").lower() if isinstance(s, dict) else getattr(s, "title", "").lower()

            if target_lower in s_type or target_lower in s_title:
                content = s.get("content", "") if isinstance(s, dict) else getattr(s, "content", "")
                title = s.get("title", "") if isinstance(s, dict) else getattr(s, "title", "")
                matched.append({"title": title, "type": s_type, "content": content})

        if not matched and raw_text:
            import re
            pattern = re.compile(rf"(?:#+\s*|(?:\d+\.?\s*))({target_type}[^\n]*)\n(.*?)(?=\n#|\n\d+\.|\Z)", re.IGNORECASE | re.DOTALL)
            for m in pattern.finditer(raw_text):
                matched.append({"title": m.group(1).strip(), "type": target_type, "content": m.group(2).strip()})

        return ToolResult(
            success=True,
            data={
                "target_type": target_type,
                "matches_found": len(matched),
                "sections": matched,
            },
        )

    def _extract_benchmarks(self, paper_struct: Dict[str, Any], raw_text: str) -> ToolResult:
        tables = paper_struct.get("tables", [])
        benchmark_tables = []

        for tbl in tables:
            headers = tbl.get("headers", []) if isinstance(tbl, dict) else getattr(tbl, "headers", [])
            headers_lower = [h.lower() for h in headers]
            # Check if table headers look like benchmark evaluation metrics
            if any(k in " ".join(headers_lower) for k in ["dataset", "benchmark", "accuracy", "f1", "bleu", "score", "baseline", "model"]):
                rows = tbl.get("rows", []) if isinstance(tbl, dict) else getattr(tbl, "rows", [])
                caption = tbl.get("caption", "") if isinstance(tbl, dict) else getattr(tbl, "caption", "")
                benchmark_tables.append({"caption": caption, "headers": headers, "rows": rows})

        return ToolResult(
            success=True,
            data={
                "benchmark_tables_count": len(benchmark_tables),
                "benchmarks": benchmark_tables,
            },
        )


class MethodologyComparisonTool(BaseTool):
    """Tool for cross-paper methodology comparison, benchmark performance diffs, and trade-off synthesis."""

    @property
    def name(self) -> str:
        return "methodology_comparison"

    @property
    def description(self) -> str:
        return (
            "Compares 2 or more research papers across core dimensions: "
            "Problem Formulation, Proposed Architecture, Baseline Models, Evaluation Benchmarks, "
            "Metric Scores, Performance Deltas, and Stated Limitations."
        )

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "papers": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of paper summary objects containing 'title', 'methodology', 'benchmarks', 'results', 'limitations'.",
                },
                "comparison_focus": {
                    "type": "string",
                    "enum": ["all", "methodology", "benchmarks", "limitations"],
                    "description": "Primary dimension for the comparative matrix.",
                    "default": "all",
                },
            },
            "required": ["papers"],
        }

    async def execute(self, **kwargs: Any) -> ToolResult:
        papers: List[Dict[str, Any]] = kwargs.get("papers") or []
        focus: str = kwargs.get("comparison_focus", "all")

        if not papers or len(papers) < 2:
            return ToolResult(
                success=False,
                error="methodology_comparison requires at least 2 papers to generate a comparative matrix.",
            )

        try:
            matrix = self._generate_matrix(papers, focus)
            return ToolResult(success=True, data=matrix)
        except Exception as e:
            logger.error("MethodologyComparisonTool execution failed", error=str(e))
            return ToolResult(success=False, error=f"MethodologyComparison error: {str(e)}")

    def _generate_matrix(self, papers: List[Dict[str, Any]], focus: str) -> Dict[str, Any]:
        paper_summaries = []
        for p in papers:
            title = p.get("title") or p.get("name", "Untitled Paper")
            method = p.get("methodology") or p.get("method", "Not specified")
            benchmarks = p.get("benchmarks") or p.get("datasets", [])
            results = p.get("results") or p.get("metrics", {})
            limitations = p.get("limitations") or p.get("weaknesses", "None stated")

            paper_summaries.append({
                "title": title,
                "methodology": method,
                "benchmarks": benchmarks,
                "results": results,
                "limitations": limitations,
            })

        # Build Markdown Comparative Table
        md_lines = [
            "### Cross-Paper Methodology & Benchmark Comparison Matrix",
            "",
            "| Dimension | " + " | ".join(f"**{p['title']}**" for p in paper_summaries) + " |",
            "|---| " + " | ".join(["---"] * len(paper_summaries)) + " |",
            "| **Core Architecture** | " + " | ".join(str(p["methodology"])[:120] for p in paper_summaries) + " |",
            "| **Evaluated Datasets** | " + " | ".join(str(p["benchmarks"])[:120] for p in paper_summaries) + " |",
            "| **Key Empirical Results** | " + " | ".join(str(p["results"])[:120] for p in paper_summaries) + " |",
            "| **Stated Limitations** | " + " | ".join(str(p["limitations"])[:120] for p in paper_summaries) + " |",
        ]

        markdown_table = "\n".join(md_lines)

        return {
            "paper_count": len(paper_summaries),
            "papers": paper_summaries,
            "comparison_matrix_markdown": markdown_table,
            "focus": focus,
        }
