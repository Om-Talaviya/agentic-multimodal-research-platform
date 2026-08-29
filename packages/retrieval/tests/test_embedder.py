"""Unit tests for Embedder service."""

import math
from unittest.mock import AsyncMock, MagicMock
import pytest
from ai.schemas import EmbeddingResponse
from retrieval.embedder import Embedder, deterministic_mock_embedding, normalize_vector


def test_normalize_vector():
    v = [3.0, 4.0]
    norm = normalize_vector(v)
    assert len(norm) == 2
    length = math.sqrt(norm[0] ** 2 + norm[1] ** 2)
    assert pytest.approx(length, 1e-6) == 1.0


def test_normalize_zero_vector():
    v = [0.0, 0.0]
    assert normalize_vector(v) == [0.0, 0.0]
    assert normalize_vector([]) == []


def test_deterministic_mock_embedding():
    emb1 = deterministic_mock_embedding("multimodal AI research", 768)
    emb2 = deterministic_mock_embedding("multimodal AI research", 768)
    emb3 = deterministic_mock_embedding("different query string", 768)

    assert len(emb1) == 768
    assert emb1 == emb2  # Determinism
    assert emb1 != emb3  # Divergence

    length = math.sqrt(sum(x * x for x in emb1))
    assert pytest.approx(length, 1e-6) == 1.0


@pytest.mark.asyncio
async def test_embedder_fallback():
    embedder = Embedder(dimensions=128, batch_size=2)
    texts = ["doc 1", "doc 2", "doc 3"]
    embs = await embedder.embed_batch(texts)

    assert len(embs) == 3
    assert len(embs[0]) == 128
    assert len(embs[1]) == 128
    assert len(embs[2]) == 128


@pytest.mark.asyncio
async def test_embedder_with_provider():
    mock_provider = MagicMock()
    mock_provider.embed = AsyncMock(
        return_value=EmbeddingResponse(
            embeddings=[[0.6, 0.8], [1.0, 0.0]],
            model="nomic-embed-text",
        )
    )

    embedder = Embedder(provider=mock_provider)
    embs = await embedder.embed_batch(["text A", "text B"])

    assert len(embs) == 2
    assert pytest.approx(embs[0][0], 1e-5) == 0.6
    assert pytest.approx(embs[0][1], 1e-5) == 0.8
