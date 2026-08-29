"""Unit tests for InMemoryVectorStore."""

import tempfile
from pathlib import Path
import pytest
from retrieval.in_memory_store import InMemoryVectorStore, cosine_similarity
from retrieval.vector_store import VectorDocument


def test_cosine_similarity():
    assert pytest.approx(cosine_similarity([1.0, 0.0], [1.0, 0.0]), 1e-6) == 1.0
    assert pytest.approx(cosine_similarity([1.0, 0.0], [0.0, 1.0]), 1e-6) == 0.0
    assert pytest.approx(cosine_similarity([1.0, 0.0], [-1.0, 0.0]), 1e-6) == -1.0
    assert cosine_similarity([], []) == 0.0
    assert cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0


@pytest.mark.asyncio
async def test_in_memory_vector_store_crud_and_search():
    store = InMemoryVectorStore()

    doc1 = VectorDocument(
        id="doc_1",
        content="Deep learning transformers for multimodal AI",
        embedding=[1.0, 0.0, 0.0],
        metadata={"modality": "text", "job_id": "job_100"},
    )
    doc2 = VectorDocument(
        id="doc_2",
        content="Computer vision CNNs for image classification",
        embedding=[0.0, 1.0, 0.0],
        metadata={"modality": "image", "job_id": "job_100"},
    )
    doc3 = VectorDocument(
        id="doc_3",
        content="Reinforcement learning from human feedback",
        embedding=[0.707, 0.707, 0.0],
        metadata={"modality": "text", "job_id": "job_200"},
    )

    await store.add([doc1, doc2, doc3])
    assert await store.count() == 3

    # Search with query vector closest to doc1
    results = await store.search(query_vector=[1.0, 0.0, 0.0], top_k=2)
    assert len(results) == 2
    assert results[0].id == "doc_1"
    assert pytest.approx(results[0].score, 1e-5) == 1.0
    assert results[1].id == "doc_3"

    # Search with metadata filter
    filtered = await store.search(query_vector=[1.0, 0.0, 0.0], top_k=5, filter={"job_id": "job_200"})
    assert len(filtered) == 1
    assert filtered[0].id == "doc_3"

    # Get single document
    fetched = await store.get("doc_2")
    assert fetched is not None
    assert fetched.content == doc2.content

    # Delete
    await store.delete(["doc_2"])
    assert await store.count() == 2
    assert await store.get("doc_2") is None

    # Clear
    await store.clear()
    assert await store.count() == 0


@pytest.mark.asyncio
async def test_in_memory_persistence():
    with tempfile.TemporaryDirectory() as tmp_dir:
        persist_file = Path(tmp_dir) / "vectors.json"
        store1 = InMemoryVectorStore(persist_path=persist_file)

        doc = VectorDocument(
            id="saved_doc",
            content="Persistent knowledge chunk",
            embedding=[0.5, 0.5],
            metadata={"source": "test"},
        )
        await store1.add([doc])
        assert persist_file.exists()

        # Load into a second store instance
        store2 = InMemoryVectorStore(persist_path=persist_file)
        assert await store2.count() == 1
        retrieved = await store2.get("saved_doc")
        assert retrieved is not None
        assert retrieved.content == "Persistent knowledge chunk"
