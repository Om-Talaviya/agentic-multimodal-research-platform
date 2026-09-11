"""Tests for Phase 9 Intelligent Knowledge Automation and Auto-Indexing."""

import io
from unittest.mock import AsyncMock, MagicMock
import pytest
from ingestion.chunking import FixedSizeChunker, SemanticChunker
from ingestion.pipeline import IngestionPipeline
from retrieval.bm25 import BM25Index
from retrieval.in_memory_store import InMemoryVectorStore
from retrieval.indexer import KnowledgeIndexer
from retrieval.embedder import Embedder


class MockEmbedder(Embedder):
    """Mock embedder returning deterministic unit vectors."""
    def __init__(self):
        super().__init__()

    async def embed_text(self, text: str):
        return [0.1, 0.2, 0.3, 0.4]

    async def embed_batch(self, texts):
        return [[0.1, 0.2, 0.3, 0.4] for _ in texts]


@pytest.mark.asyncio
async def test_ingestion_pipeline_with_auto_indexing():
    vector_store = InMemoryVectorStore()
    bm25_index = BM25Index()
    embedder = MockEmbedder()
    indexer = KnowledgeIndexer(
        vector_store=vector_store,
        bm25_index=bm25_index,
        embedder=embedder,
    )

    mock_repo = MagicMock()
    mock_repo.create = AsyncMock()
    mock_repo.create_chunks = AsyncMock()
    mock_repo.update_status = AsyncMock()

    pipeline = IngestionPipeline(
        chunker=SemanticChunker(max_chunk_size=500, min_chunk_size=30),
        doc_repo=mock_repo,
        indexer=indexer,
    )

    sample_text = (
        "# Solid-State Battery Research\n\n"
        "Solid-state lithium batteries offer enhanced energy density and thermal safety compared to conventional liquid electrolytes.\n\n"
        "Silicon anode materials can achieve theoretical capacities exceeding 3500 mAh/g."
    )
    file_obj = io.BytesIO(sample_text.encode("utf-8"))

    result = await pipeline.ingest(
        file=file_obj,
        filename="battery_study.md",
        mime_type="text/markdown",
    )

    assert result.filename == "battery_study.md"
    assert result.status == "ready"
    assert result.indexed_chunk_count > 0
    assert len(result.chunks) == result.indexed_chunk_count

    # Verify vector store contains chunks
    assert await vector_store.count() == result.indexed_chunk_count

    # Verify BM25 index contains search terms
    search_results = bm25_index.search("electrolyte lithium", top_k=2)
    assert len(search_results) > 0
    assert any("electrolyte" in r.content.lower() for r in search_results)

    # Verify status updates in mock repo
    assert mock_repo.create.await_count == 1
    assert mock_repo.create_chunks.await_count == 1
    assert mock_repo.update_status.await_count == 1
    call_args = mock_repo.update_status.call_args[1]
    assert call_args["status"] == "ready"


@pytest.mark.asyncio
async def test_indexer_delete_document():
    vector_store = InMemoryVectorStore()
    bm25_index = BM25Index()
    embedder = MockEmbedder()
    indexer = KnowledgeIndexer(
        vector_store=vector_store,
        bm25_index=bm25_index,
        embedder=embedder,
    )

    chunks = [
        {"id": "chunk_1", "document_id": "doc_123", "content": "Microplastics in ocean water", "metadata": {"page": 1}},
        {"id": "chunk_2", "document_id": "doc_123", "content": "Filtration membrane pore size", "metadata": {"page": 2}},
    ]

    indexed_count = await indexer.index_chunks(chunks, document_id="doc_123", filename="ocean.pdf")
    assert indexed_count == 2
    assert await vector_store.count() == 2

    # Direct delete test on store
    await vector_store.delete(["chunk_1", "chunk_2"])
    bm25_index.delete(["chunk_1", "chunk_2"])

    assert await vector_store.count() == 0
    search_after = bm25_index.search("Microplastics", top_k=5)
    assert len(search_after) == 0
