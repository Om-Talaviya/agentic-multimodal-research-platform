"""Tests for IngestionPipeline orchestration."""

import io
from unittest.mock import AsyncMock, MagicMock
import pytest
from ingestion.chunking import FixedSizeChunker
from ingestion.parsers.registry import ParserRegistry
from ingestion.pipeline import IngestionPipeline


@pytest.mark.asyncio
async def test_ingestion_pipeline_without_db():
    pipeline = IngestionPipeline(
        chunker=FixedSizeChunker(chunk_size=20, overlap=5),
    )

    file_obj = io.BytesIO(b"This is a sample document for testing the multimodal ingestion pipeline.")
    result = await pipeline.ingest(file_obj, "test_doc.txt")

    assert result.filename == "test_doc.txt"
    assert len(result.chunks) >= 3
    assert result.table_count == 0
    assert result.image_count == 0
    assert result.document_id is not None
    assert result.metadata["chunk_count"] == len(result.chunks)


@pytest.mark.asyncio
async def test_ingestion_pipeline_with_mock_db():
    mock_repo = MagicMock()
    mock_repo.create = AsyncMock()
    mock_repo.create_chunks = AsyncMock()

    pipeline = IngestionPipeline(
        doc_repo=mock_repo,
    )

    file_obj = io.BytesIO(b"# Research Paper\n\nParagraph 1.\n\nParagraph 2.")
    result = await pipeline.ingest(file_obj, "paper.md", research_job_id="11111111-1111-1111-1111-111111111111")

    assert result.filename == "paper.md"
    assert len(result.chunks) >= 1
    assert mock_repo.create.await_count == 1
    assert mock_repo.create_chunks.await_count == 1
