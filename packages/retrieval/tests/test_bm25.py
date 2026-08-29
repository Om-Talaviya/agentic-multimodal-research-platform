"""Unit tests for BM25 lexical search index."""

import pytest
from retrieval.bm25 import BM25Index, tokenize


def test_tokenize():
    text = "Hello, World! Tokenize 123 multimodal_AI."
    tokens = tokenize(text)
    assert tokens == ["hello", "world", "tokenize", "123", "multimodal_ai"]
    assert tokenize("") == []
    assert tokenize(None) == []


def test_bm25_search_and_ranking():
    index = BM25Index()

    docs = [
        {"id": "doc_1", "content": "Transformer models enable attention across multimodal sequence inputs.", "metadata": {"category": "nlp"}},
        {"id": "doc_2", "content": "Convolutional networks are used for image processing and edge detection.", "metadata": {"category": "cv"}},
        {"id": "doc_3", "content": "Multimodal attention networks combine transformer encoders and image convolutional layers.", "metadata": {"category": "multimodal"}},
    ]

    index.add_batch(docs)
    assert index.count() == 3

    # Query for "transformer attention"
    results = index.search(query="transformer attention", top_k=2)
    assert len(results) == 2
    top_ids = [r.id for r in results]
    assert "doc_1" in top_ids or "doc_3" in top_ids

    # Query with category filter
    filtered = index.search(query="image", top_k=5, filter={"category": "cv"})
    assert len(filtered) == 1
    assert filtered[0].id == "doc_2"

    # Delete
    index.delete(["doc_2"])
    assert index.count() == 2
    deleted_search = index.search(query="convolutional edge", top_k=5)
    assert len(deleted_search) == 1  # only doc_3 remains with convolutional

    # Empty query
    assert index.search(query="", top_k=5) == []

    # Clear
    index.clear()
    assert index.count() == 0
