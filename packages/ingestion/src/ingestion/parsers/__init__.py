"""Document parsers package."""

from ingestion.parsers.audio import AudioParser
from ingestion.parsers.base import (
    AudioSegment,
    ChartRef,
    ColumnProfile,
    DatasetProfile,
    DocumentParser,
    ImageRef,
    ParsedDocument,
    Table,
)
from ingestion.parsers.docx import DocxParser
from ingestion.parsers.image import ImageParser
from ingestion.parsers.pdf import PDFParser
from ingestion.parsers.registry import ParserRegistry
from ingestion.parsers.tabular import TabularParser
from ingestion.parsers.text import TextParser
from ingestion.parsers.video import VideoParser

__all__ = [
    "DocumentParser",
    "ParsedDocument",
    "ImageRef",
    "Table",
    "AudioSegment",
    "ChartRef",
    "ColumnProfile",
    "DatasetProfile",
    "TextParser",
    "PDFParser",
    "DocxParser",
    "TabularParser",
    "ImageParser",
    "AudioParser",
    "VideoParser",
    "ParserRegistry",
]


