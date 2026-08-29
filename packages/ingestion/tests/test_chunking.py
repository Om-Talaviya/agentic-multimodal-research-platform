"""Tests for chunking strategies."""

import pytest
from ingestion.chunking import FixedSizeChunker, SemanticChunker
from ingestion.parsers.base import ParsedDocument


def test_fixed_size_chunker_basic():
    chunker = FixedSizeChunker(chunk_size=50, overlap=10)
    text = "A" * 120
    doc = ParsedDocument(content=text, metadata={"filename": "test.txt"})

    chunks = chunker.chunk(doc)
    assert len(chunks) == 3
    assert chunks[0].start_char == 0
    assert chunks[0].end_char == 50
    assert chunks[1].start_char == 40
    assert chunks[1].end_char == 90
    assert chunks[2].start_char == 80
    assert chunks[2].end_char == 120


def test_fixed_size_chunker_invalid_overlap():
    with pytest.raises(ValueError):
        FixedSizeChunker(chunk_size=100, overlap=100)


def test_semantic_chunker_paragraphs():
    chunker = SemanticChunker(max_chunk_size=100)
    p1 = "First paragraph content that is relatively short."
    p2 = "Second paragraph content that also fits within limit."
    p3 = "Third paragraph content that pushes the chunk over max size."
    full_text = f"{p1}\n\n{p2}\n\n{p3}"

    doc = ParsedDocument(content=full_text, metadata={"filename": "doc.md"})
    chunks = chunker.chunk(doc)

    assert len(chunks) >= 2
    for chunk in chunks:
        assert len(chunk.content) <= 150  # Allows boundary padding
        assert chunk.metadata["filename"] == "doc.md"


def test_semantic_chunker_empty():
    chunker = SemanticChunker()
    doc = ParsedDocument(content="", metadata={"filename": "empty.txt"})
    assert chunker.chunk(doc) == []
