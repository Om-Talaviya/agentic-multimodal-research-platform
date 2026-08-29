"""Tests for PDF parser."""

import io
import sys
from unittest.mock import MagicMock, patch
import pytest
from ingestion.parsers.pdf import PDFParser
from shared.types import DocumentFormat


@pytest.mark.asyncio
async def test_pdf_parser_with_mocked_pdfplumber():
    parser = PDFParser()
    assert DocumentFormat.PDF in parser.supported_formats

    # Create mock page with text and table
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "Page 1 intro text."
    mock_page.extract_tables.return_value = [
        [["Header A", "Header B"], ["Val 1", "Val 2"]]
    ]

    mock_pdf = MagicMock()
    mock_pdf.pages = [mock_page]
    mock_pdf.metadata = {"Author": "Researcher"}
    mock_pdf.__enter__.return_value = mock_pdf

    mock_pdfplumber = MagicMock()
    mock_pdfplumber.open.return_value = mock_pdf

    with patch.dict(sys.modules, {"pdfplumber": mock_pdfplumber}):
        file_obj = io.BytesIO(b"%PDF-1.4 dummy pdf bytes")
        parsed = await parser.parse(file_obj, "paper.pdf")

        assert "[Page 1]" in parsed.content
        assert "Page 1 intro text." in parsed.content
        assert len(parsed.tables) == 1
        assert parsed.tables[0].headers == ["Header A", "Header B"]
        assert parsed.tables[0].rows == [["Val 1", "Val 2"]]
        assert "| Header A | Header B |" in parsed.content
        assert parsed.metadata["format"] == "pdf"
        assert parsed.metadata["page_count"] == 1
        assert parsed.metadata["pdf_metadata"] == {"Author": "Researcher"}


@pytest.mark.asyncio
async def test_pdf_parser_raises_when_pdfplumber_missing():
    parser = PDFParser()
    with patch.dict(sys.modules, {"pdfplumber": None}):
        file_obj = io.BytesIO(b"%PDF-1.4 dummy pdf bytes")
        with pytest.raises(ImportError) as exc_info:
            await parser.parse(file_obj, "paper.pdf")
        assert "pdfplumber is required" in str(exc_info.value)
