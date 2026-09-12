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
class ParsedDocument:
    """Normalized result of parsing a document."""

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    images: List[ImageRef] = field(default_factory=list)
    tables: List[Table] = field(default_factory=list)
    audio_segments: List[AudioSegment] = field(default_factory=list)
    charts: List[ChartRef] = field(default_factory=list)
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
