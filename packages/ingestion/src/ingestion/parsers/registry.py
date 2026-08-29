"""Registry for managing and dispatching document parsers."""

from typing import BinaryIO, List, Optional, Union
from ai.gateway.model_gateway import ModelGateway
from ai.providers.base import VisionProvider
from ai.providers.router import ModelRouter
from ingestion.detection import detect_format
from ingestion.parsers.base import DocumentParser, ParsedDocument
from ingestion.parsers.docx import DocxParser
from ingestion.parsers.image import ImageParser
from ingestion.parsers.pdf import PDFParser
from ingestion.parsers.text import TextParser
from shared.exceptions import ValidationError
from shared.logging import get_logger
from shared.types import DocumentFormat

logger = get_logger(__name__)


class ParserRegistry:
    """Registry holding all available document parsers."""

    def __init__(
        self,
        vision_source: Optional[Union[ModelGateway, ModelRouter, VisionProvider]] = None,
        custom_parsers: Optional[List[DocumentParser]] = None,
    ) -> None:
        self._parsers: List[DocumentParser] = custom_parsers if custom_parsers is not None else [
            TextParser(),
            PDFParser(),
            DocxParser(),
            ImageParser(vision_source=vision_source),
        ]

    def register_parser(self, parser: DocumentParser) -> None:
        """Register a new custom parser (takes precedence at the front)."""
        self._parsers.insert(0, parser)

    def get_parser(self, format: DocumentFormat) -> Optional[DocumentParser]:
        """Find the first parser capable of handling the given document format."""
        for parser in self._parsers:
            if format in parser.supported_formats:
                return parser
        return None

    async def parse(
        self,
        file: BinaryIO,
        filename: str,
        mime_type: Optional[str] = None,
    ) -> ParsedDocument:
        """Detect format and parse the document using the registered parser."""
        format = detect_format(filename, mime_type)
        if format == DocumentFormat.UNKNOWN:
            # Fallback to TextParser
            format = DocumentFormat.TEXT

        parser = self.get_parser(format)
        if not parser:
            raise ValidationError(
                f"No suitable parser registered for format '{format.value}'",
                details={"filename": filename, "format": format.value, "mime_type": mime_type},
            )

        logger.debug(
            "Dispatching file to parser",
            filename=filename,
            format=format.value,
            parser=parser.__class__.__name__,
        )
        return await parser.parse(file, filename)
