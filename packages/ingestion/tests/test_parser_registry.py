"""Tests for parser registry."""

import io
from typing import BinaryIO, List
import pytest
from ingestion.parsers.base import DocumentParser, ParsedDocument
from ingestion.parsers.registry import ParserRegistry
from shared.types import DocumentFormat


class MockCustomParser(DocumentParser):
    @property
    def supported_formats(self) -> List[DocumentFormat]:
        return [DocumentFormat.TEXT]

    async def parse(self, file: BinaryIO, filename: str) -> ParsedDocument:
        return ParsedDocument(content="custom parsed", metadata={"custom": True})


@pytest.mark.asyncio
async def test_parser_registry_dispatch():
    registry = ParserRegistry()

    text_file = io.BytesIO(b"Hello world")
    parsed = await registry.parse(text_file, "sample.txt")
    assert parsed.content == "Hello world"
    assert parsed.metadata["format"] == "text"


@pytest.mark.asyncio
async def test_parser_registry_custom_parser_override():
    registry = ParserRegistry()
    registry.register_parser(MockCustomParser())

    text_file = io.BytesIO(b"Hello world")
    parsed = await registry.parse(text_file, "sample.txt")
    assert parsed.content == "custom parsed"
    assert parsed.metadata["custom"] is True
