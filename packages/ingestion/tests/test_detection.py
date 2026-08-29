"""Tests for document format detection."""

import pytest
from ingestion.detection import detect_format
from shared.types import DocumentFormat


def test_detect_format_by_extension():
    assert detect_format("doc.txt") == DocumentFormat.TEXT
    assert detect_format("README.md") == DocumentFormat.MARKDOWN
    assert detect_format("paper.pdf") == DocumentFormat.PDF
    assert detect_format("report.docx") == DocumentFormat.DOCX
    assert detect_format("photo.png") == DocumentFormat.IMAGE
    assert detect_format("photo.jpg") == DocumentFormat.IMAGE
    assert detect_format("photo.jpeg") == DocumentFormat.IMAGE
    assert detect_format("photo.webp") == DocumentFormat.IMAGE
    assert detect_format("page.html") == DocumentFormat.HTML
    assert detect_format("file.xyz") == DocumentFormat.UNKNOWN


def test_detect_format_by_mime_fallback():
    assert detect_format("unknown_file", mime_type="text/plain") == DocumentFormat.TEXT
    assert detect_format("unknown_file", mime_type="application/pdf") == DocumentFormat.PDF
    assert (
        detect_format(
            "unknown_file",
            mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        == DocumentFormat.DOCX
    )
    assert detect_format("unknown_file", mime_type="image/png") == DocumentFormat.IMAGE
    assert detect_format("unknown_file", mime_type="image/jpeg; charset=binary") == DocumentFormat.IMAGE
    assert detect_format("unknown_file", mime_type="application/octet-stream") == DocumentFormat.UNKNOWN
