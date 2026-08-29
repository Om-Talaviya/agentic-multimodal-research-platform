"""Unit tests for HybridRetriever with RRF and evidence grounding."""

import pytest
from retrieval.bm25 import BM25Index
from retrieval.embedder import Embedder
from retrieval.in_memory_store import InMemoryVectorStore
from retrieval.reranker import Reranker
from retrieval.retriever import HybridRetriever
from retrieval.vector_store import VectorDocument


@pytest.mark.asyncio
async def test_hybrid_retriever_dense_and_sparse_rrf():
    vector_store = InMemoryVectorStore()
    bm25_index = BM25Index()
    embedder = Embedder()
    reranker = Reranker()

    retriever = HybridRetriever(
        vector_store=vector_store,
        bm25_index=bm25_index,
        embedder=embedder,
        reranker=reranker,
        rrf_k=60,
    )

    # Add sample documents
    doc1 = "Document 1 discusses quantum quantum entanglement and teleportation algorithms."
    doc2 = "Document 2 is a table of multimodal benchmark metrics: Table accuracy is 94.2%."
    doc3 = "Document 3 describes autonomous agent architectures with memory and critic verification."

    emb1 = await embedder.embed_text(doc1)
    emb2 = await embedder.embed_text(doc2)
    emb3 = await embedder.embed_text(doc3)

    await vector_store.add([
        VectorDocument(id="c1", content=doc1, embedding=emb1, metadata={"document_id": "doc_100", "chunk_index": 0, "modality": "text"}),
        VectorDocument(id="c2", content=doc2, embedding=emb2, metadata={"document_id": "doc_200", "chunk_index": 1, "modality": "table"}),
        VectorDocument(id="c3", content=doc3, embedding=emb3, metadata={"document_id": "doc_300", "chunk_index": 2, "modality": "text"}),
    ])

    bm25_index.add_batch([
        {"id": "c1", "content": doc1, "metadata": {"document_id": "doc_100", "chunk_index": 0, "modality": "text"}},
        {"id": "c2", "content": doc2, "metadata": {"document_id": "doc_200", "chunk_index": 1, "modality": "table"}},
        {"id": "c3", "content": doc3, "metadata": {"document_id": "doc_300", "chunk_index": 2, "modality": "text"}},
    ])

    # Search for table metrics
    evidence = await retriever.retrieve(query="table accuracy benchmark", top_k=2)

    assert len(evidence) >= 1
    top_ev = evidence[0]
    assert top_ev.chunk_id == "c2"
    assert top_ev.modality == "table"
    assert "Doc: doc_200" in top_ev.citation
    assert top_ev.rrf_score is not None
    assert top_ev.score > 0.0


@pytest.mark.asyncio
async def test_hybrid_retriever_empty_query():
    retriever = HybridRetriever(
        vector_store=InMemoryVectorStore(),
        bm25_index=BM25Index(),
        embedder=Embedder(),
    )
    res = await retriever.retrieve(query="", top_k=5)
    assert res == []
