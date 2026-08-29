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
class ParsedDocument:
    """Normalized result of parsing a document."""

    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    images: List[ImageRef] = field(default_factory=list)
    tables: List[Table] = field(default_factory=list)
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
