"""Document parsers package."""

from ingestion.parsers.base import DocumentParser, ImageRef, ParsedDocument, Table
from ingestion.parsers.docx import DocxParser
from ingestion.parsers.image import ImageParser
from ingestion.parsers.pdf import PDFParser
from ingestion.parsers.registry import ParserRegistry
from ingestion.parsers.text import TextParser

__all__ = [
    "DocumentParser",
    "ParsedDocument",
    "ImageRef",
    "Table",
    "TextParser",
    "PDFParser",
    "DocxParser",
    "ImageParser",
    "ParserRegistry",
]
