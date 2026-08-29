"""Unit tests for ChromaVectorStore adapter."""

from unittest.mock import MagicMock
import pytest
from retrieval.chroma_store import ChromaVectorStore
from retrieval.vector_store import VectorDocument


def test_chroma_availability_check():
    store = ChromaVectorStore()
    # Should not raise exception and return boolean
    assert isinstance(store.is_available, bool)


@pytest.mark.asyncio
async def test_chroma_store_with_mock_client():
    mock_collection = MagicMock()
    mock_collection.count.return_value = 2
    mock_collection.query.return_value = {
        "ids": [["c1", "c2"]],
        "documents": [["doc 1 content", "doc 2 content"]],
        "metadatas": [[{"doc_id": "1"}, {"doc_id": "2"}]],
        "distances": [[0.1, 0.4]],
    }
    mock_collection.get.return_value = {
        "ids": ["c1"],
        "documents": ["doc 1 content"],
        "metadatas": [{"doc_id": "1"}],
        "embeddings": [[1.0, 0.0]],
    }

    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection

    store = ChromaVectorStore(client=mock_client)
    assert await store.count() == 2

    # Add
    doc = VectorDocument(id="c1", content="doc 1 content", embedding=[1.0, 0.0], metadata={"doc_id": "1"})
    await store.add([doc])
    mock_collection.upsert.assert_called_once()

    # Search
    results = await store.search(query_vector=[1.0, 0.0], top_k=2)
    assert len(results) == 2
    assert results[0].id == "c1"
    assert pytest.approx(results[0].score, 1e-5) == 0.9

    # Get
    fetched = await store.get("c1")
    assert fetched is not None
    assert fetched.content == "doc 1 content"

    # Delete
    await store.delete(["c1"])
    mock_collection.delete.assert_called_once_with(ids=["c1"])
