"""Parser for plain text, markdown, and HTML documents."""

from typing import BinaryIO, List
from ingestion.parsers.base import DocumentParser, ParsedDocument
from shared.types import DocumentFormat


class TextParser(DocumentParser):
    """Parse plain text, markdown, and HTML files."""

    @property
    def supported_formats(self) -> List[DocumentFormat]:
        return [DocumentFormat.TEXT, DocumentFormat.MARKDOWN, DocumentFormat.HTML]

    async def parse(self, file: BinaryIO, filename: str) -> ParsedDocument:
        raw = file.read()
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            content = raw.decode("latin-1", errors="replace")

        fmt = "text"
        if filename.lower().endswith((".md", ".markdown")):
            fmt = "markdown"
        elif filename.lower().endswith((".html", ".htm")):
            fmt = "html"

        metadata = {
            "format": fmt,
            "filename": filename,
            "char_count": len(content),
            "byte_size": len(raw),
        }

        return ParsedDocument(
            content=content,
            metadata=metadata,
        )
