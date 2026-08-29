"""Tests for text parser."""

import io
import pytest
from ingestion.parsers.text import TextParser
from shared.types import DocumentFormat


@pytest.mark.asyncio
async def test_text_parser_plain_text():
    parser = TextParser()
    assert DocumentFormat.TEXT in parser.supported_formats

    content = b"Hello, this is plain text content."
    file_obj = io.BytesIO(content)

    doc = await parser.parse(file_obj, "test.txt")
    assert doc.content == "Hello, this is plain text content."
    assert doc.metadata["format"] == "text"
    assert doc.metadata["char_count"] == len(doc.content)


@pytest.mark.asyncio
async def test_text_parser_markdown():
    parser = TextParser()
    content = b"# Title\n\nThis is **markdown** content."
    file_obj = io.BytesIO(content)

    doc = await parser.parse(file_obj, "notes.md")
    assert doc.content == "# Title\n\nThis is **markdown** content."
    assert doc.metadata["format"] == "markdown"
