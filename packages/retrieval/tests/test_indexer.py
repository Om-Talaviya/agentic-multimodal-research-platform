"""Unit tests for KnowledgeIndexer service."""

from uuid import uuid4
import pytest
from retrieval.bm25 import BM25Index
from retrieval.embedder import Embedder
from retrieval.in_memory_store import InMemoryVectorStore
from retrieval.indexer import KnowledgeIndexer


@pytest.mark.asyncio
async def test_knowledge_indexer_chunks():
    vector_store = InMemoryVectorStore()
    bm25_index = BM25Index()
    embedder = Embedder()

    indexer = KnowledgeIndexer(
        vector_store=vector_store,
        bm25_index=bm25_index,
        embedder=embedder,
    )

    doc_id = str(uuid4())
    chunks = [
        {
            "id": "chunk_1",
            "document_id": doc_id,
            "content": "Section 1: Ingestion pipeline architectures.",
            "chunk_metadata": {"type": "text", "page": 1},
            "chunk_index": 0,
        },
        {
            "id": "chunk_2",
            "document_id": doc_id,
            "content": "| Engine | Accuracy |\n| GPT-4 | 92% |",
            "chunk_metadata": {"type": "table", "table_markdown": True},
            "chunk_index": 1,
        },
    ]

    indexed_count = await indexer.index_chunks(chunks, document_id=doc_id, filename="architecture.pdf")

    assert indexed_count == 2
    assert await vector_store.count() == 2
    assert bm25_index.count() == 2

    # Verify vector store document contains multimodal metadata
    vdoc = await vector_store.get("chunk_2")
    assert vdoc is not None
    assert vdoc.metadata["modality"] == "table"
    assert vdoc.metadata["filename"] == "architecture.pdf"
    assert vdoc.metadata["document_id"] == doc_id
