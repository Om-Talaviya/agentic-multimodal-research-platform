"""Base classes and data models for document parsers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, BinaryIO, Dict, List, Optional, Tuple
from shared.types import DocumentFormat


@dataclass
class ImageRef:
    """Reference to an image within a document or parsed input."""

    id: str
    data: Optional[bytes] = None
    path: Optional[str] = None
    mime_type: str = "image/png"
    caption: Optional[str] = None
    page_number: Optional[int] = None
    bbox: Optional[Tuple[float, float, float, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Table:
    """Extracted table data from a document."""

    id: str
    headers: List[str]
    rows: List[List[str]]
    page_number: Optional[int] = None
    caption: Optional[str] = None
    format: str = "csv"  # csv, markdown, json
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_markdown(self) -> str:
        """Render table as a markdown string."""
        if not self.headers and not self.rows:
            return ""

        headers = self.headers if self.headers else [f"Col {i+1}" for i in range(len(self.rows[0]))] if self.rows else []
        col_count = len(headers)

        lines = []
        if self.caption:
            lines.append(f"**Table: {self.caption}**\n")

        # Header row
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * col_count) + " |")

        # Data rows
        for row in self.rows:
            padded_row = list(row) + [""] * (col_count - len(row))
            lines.append("| " + " | ".join(padded_row[:col_count]) + " |")

        return "\n".join(lines)


@dataclass
class AudioSegment:
    """Timestamped speech segment from an audio/video transcription."""

    start_seconds: float
    end_seconds: float
    text: str
    speaker: Optional[str] = None
    confidence: float = 0.9
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChartRef:
    """Structured extraction of a scientific chart, plot, or technical diagram."""

    id: str
    chart_type: str  # bar_chart, line_chart, scatter_plot, heatmap, architecture_diagram, flowchart
    title: str
    data_series: Dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    page_number: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_markdown(self) -> str:
        """Render chart data as markdown table or structured block."""
        parts = [f"**Chart: {self.title}** ({self.chart_type})"]
        if self.summary:
            parts.append(f"*{self.summary}*")
        if self.data_series:
            import json
            parts.append(f"```json\n{json.dumps(self.data_series, indent=2)}\n```")
        return "\n\n".join(parts)


@dataclass
class ColumnProfile:
    """Statistical profile of a tabular column."""

    name: str
    data_type: str  # integer, float, string, boolean, datetime
    total_count: int
    null_count: int
    unique_count: int
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    mean_value: Optional[float] = None
    median_value: Optional[float] = None
    std_dev: Optional[float] = None
    sample_values: List[Any] = field(default_factory=list)


@dataclass
class DatasetProfile:
    """Complete structural and statistical profile of a dataset."""

    id: str
    total_rows: int
    total_cols: int
    columns: List[ColumnProfile] = field(default_factory=list)
    sample_rows: List[Dict[str, Any]] = field(default_factory=list)
    summary_text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_markdown(self) -> str:
        """Render dataset statistical summary as markdown."""
        lines = [
            f"**Dataset Overview: {self.metadata.get('filename', 'Dataset')}**",
            f"- **Rows**: {self.total_rows} | **Columns**: {self.total_cols}",
            "",
            "### Column Profiles & Statistics",
            "| Column | Type | Nulls | Unique | Mean / Range |",
            "|---|---|---|---|---|",
        ]
        for col in self.columns:
            stat_str = "-"
            if col.mean_value is not None:
                stat_str = f"Mean: {col.mean_value:.2f} (Min: {col.min_value}, Max: {col.max_value})"
            elif col.min_value is not None and col.max_value is not None:
                stat_str = f"Range: [{col.min_value} .. {col.max_value}]"
            lines.append(f"| `{col.name}` | {col.data_type} | {col.null_count} | {col.unique_count} | {stat_str} |")

        if self.sample_rows:
            lines.append("\n### Sample Data Preview (First 5 Rows)")
            headers = [c.name for c in self.columns]
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
            for r in self.sample_rows[:5]:
                vals = [str(r.get(h, "")) for h in headers]
                lines.append("| " + " | ".join(vals) + " |")

        return "\n".join(lines)


@dataclass
class PaperSection:
    """Structural section node of an academic research paper."""

    section_id: str
    title: str
    level: int  # 1 = H1 (e.g. Introduction), 2 = H2 (e.g. 3.1 Model), 3 = H3
    section_type: str  # abstract, introduction, related_work, methodology, experiments, results, discussion, conclusion, limitations, references, appendix, other
    content: str
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    subsections: List["PaperSection"] = field(default_factory=list)
    citations_referenced: List[str] = field(default_factory=list)  # e.g. ["[1]", "[4]"]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BibEntry:
    """Bibliographic citation entry from an academic paper reference list."""

    id: str
    citation_key: str  # e.g. "[1]" or "Vaswani2017"
    raw_text: str
    authors: List[str] = field(default_factory=list)
    title: Optional[str] = None
    year: Optional[int] = None
    venue: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    url: Optional[str] = None


@dataclass
class PaperStructure:
    """Comprehensive parsed hierarchy and semantics of an academic paper."""

    id: str
    title: str
    authors: List[str] = field(default_factory=list)
    affiliations: List[str] = field(default_factory=list)
    abstract: str = ""
    sections: List[PaperSection] = field(default_factory=list)
    bibliography: List[BibEntry] = field(default_factory=list)
    benchmarks: List[Dict[str, Any]] = field(default_factory=list)
    methodology_summary: str = ""
    limitations_summary: str = ""
    tables: List[Table] = field(default_factory=list)
    charts: List[ChartRef] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_markdown(self) -> str:
        """Render complete academic paper outline and content as structured markdown."""
        lines = [
            f"# {self.title}",
            f"**Authors**: {', '.join(self.authors) if self.authors else 'Unknown'}",
        ]
        if self.affiliations:
            lines.append(f"**Affiliations**: {', '.join(self.affiliations)}")
        if self.abstract:
            lines.extend(["\n## Abstract", self.abstract])

        for sec in self.sections:
            prefix = "#" * min(sec.level + 1, 5)
            lines.append(f"\n{prefix} {sec.title}")
            if sec.content:
                lines.append(sec.content)

        if self.limitations_summary:
            lines.extend(["\n## Limitations & Assumptions", self.limitations_summary])

        if self.bibliography:
            lines.append("\n## References")
            for bib in self.bibliography:
                lines.append(f"- **{bib.citation_key}** {bib.raw_text}")

        return "\n".join(lines)


@dataclass
class ParsedDocument:
    """Normalized result of parsing a document."""

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    images: List[ImageRef] = field(default_factory=list)
    tables: List[Table] = field(default_factory=list)
    audio_segments: List[AudioSegment] = field(default_factory=list)
    charts: List[ChartRef] = field(default_factory=list)
    dataset_profile: Optional[DatasetProfile] = None
    paper_structure: Optional[PaperStructure] = None
    structure: Dict[str, Any] = field(default_factory=dict)



class DocumentParser(ABC):
    """Abstract base class for all document parsers."""

    @property
    @abstractmethod
    def supported_formats(self) -> List[DocumentFormat]:
        """Return list of formats supported by this parser."""
        pass

    @abstractmethod
    async def parse(self, file: BinaryIO, filename: str) -> ParsedDocument:
        """Parse file into a normalized ParsedDocument object."""
        pass
