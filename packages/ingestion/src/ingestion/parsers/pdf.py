"""PDF parser using pdfplumber with text and table extraction."""

import asyncio
from typing import BinaryIO, List
from uuid import uuid4
from ingestion.parsers.base import DocumentParser, ParsedDocument, Table
from shared.logging import get_logger
from shared.types import DocumentFormat

logger = get_logger(__name__)


class PDFParser(DocumentParser):
    """Parse PDF documents with text and table extraction."""

    @property
    def supported_formats(self) -> List[DocumentFormat]:
        return [DocumentFormat.PDF]

    async def parse(self, file: BinaryIO, filename: str) -> ParsedDocument:
        return await asyncio.to_thread(self._parse_sync, file, filename)

    def _parse_sync(self, file: BinaryIO, filename: str) -> ParsedDocument:
        try:
            import pdfplumber
        except ImportError as e:
            logger.error("pdfplumber is not installed. Cannot parse PDF files.", error=str(e))
            raise ImportError(
                "pdfplumber is required to parse PDF files. Please install it with 'pip install pdfplumber'."
            ) from e

        content_parts: List[str] = []
        tables: List[Table] = []

        try:
            with pdfplumber.open(file) as pdf:
                page_count = len(pdf.pages)
                metadata = {
                    "format": "pdf",
                    "filename": filename,
                    "page_count": page_count,
                    "pdf_metadata": dict(pdf.metadata or {}),
                }

                for page_num, page in enumerate(pdf.pages, 1):
                    # 1. Extract text from page
                    text = page.extract_text()
                    if text and text.strip():
                        content_parts.append(f"[Page {page_num}]\n{text.strip()}")

                    # 2. Extract tables from page
                    try:
                        page_tables = page.extract_tables()
                        for table_idx, table_data in enumerate(page_tables or []):
                            if table_data and len(table_data) > 1:
                                # Header is the first row
                                headers = [str(c).strip() if c is not None else "" for c in table_data[0]]
                                rows = [
                                    [str(c).strip() if c is not None else "" for c in row]
                                    for row in table_data[1:]
                                ]
                                table = Table(
                                    id=str(uuid4()),
                                    headers=headers,
                                    rows=rows,
                                    page_number=page_num,
                                    caption=f"Table {table_idx + 1} (Page {page_num})",
                                    metadata={"table_index": table_idx},
                                )
                                tables.append(table)
                                content_parts.append(f"\n{table.to_markdown()}\n")
                    except Exception as tbl_err:
                        logger.warning("Failed to extract tables from PDF page", page=page_num, error=str(tbl_err))

            full_content = "\n\n".join(content_parts)
            return ParsedDocument(
                content=full_content,
                metadata=metadata,
                tables=tables,
            )
        except Exception as e:
            if not isinstance(e, ImportError):
                logger.error("Failed to parse PDF document", filename=filename, error=str(e))
            raise
