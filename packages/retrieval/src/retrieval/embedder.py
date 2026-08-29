"""Embedding pipeline for text passages and multimodal chunk descriptions."""

import hashlib
import math
from typing import List, Optional
from ai.providers.base import EmbeddingProvider
from ai.providers.router import ModelRouter
from ai.schemas import EmbeddingRequest
from shared.config import settings
from shared.logging import get_logger

logger = get_logger(__name__)


def normalize_vector(v: List[float]) -> List[float]:
    """Normalize a vector to unit length (L2 norm)."""
    if not v:
        return []
    norm = math.sqrt(sum(x * x for x in v))
    if norm == 0.0:
        return v
    return [x / norm for x in v]


def deterministic_mock_embedding(text: str, dimensions: int = 768) -> List[float]:
    """Generate a deterministic normalized embedding for testing/offline mode."""
    # Use SHA-256 with sliding offset to generate pseudo-random floats
    raw_floats = []
    for i in range(dimensions):
        seed = f"{text}_{i}"
        h = int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:8], 16)
        # Scale to range [-1.0, 1.0]
        val = (h / 0xFFFFFFFF) * 2.0 - 1.0
        raw_floats.append(val)

    return normalize_vector(raw_floats)


class Embedder:
    """Embedder service providing batching, normalization, and model routing."""

    def __init__(
        self,
        model_router: Optional[ModelRouter] = None,
        provider: Optional[EmbeddingProvider] = None,
        default_model: Optional[str] = None,
        dimensions: int = 768,
        batch_size: int = 32,
    ) -> None:
        self.router = model_router
        self.provider = provider
        self.default_model = default_model or settings.default_embedding_model
        self.dimensions = dimensions
        self.batch_size = batch_size

    def _get_provider(self) -> Optional[EmbeddingProvider]:
        """Resolve embedding provider."""
        if self.provider is not None:
            return self.provider
        if self.router is not None:
            try:
                return self.router.select_embedding()
            except Exception as e:
                logger.debug("No embedding provider available from router", error=str(e))
                return None
        return None

    async def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        results = await self.embed_batch([text])
        return results[0] if results else []

    async def embed_batch(self, texts: List[str], batch_size: Optional[int] = None) -> List[List[float]]:
        """Embed a list of text strings in batches."""
        if not texts:
            return []

        effective_batch_size = batch_size or self.batch_size
        provider = self._get_provider()

        all_embeddings: List[List[float]] = []

        for i in range(0, len(texts), effective_batch_size):
            batch = texts[i : i + effective_batch_size]

            if provider is not None:
                try:
                    req = EmbeddingRequest(texts=batch, model=self.default_model)
                    resp = await provider.embed(req)
                    if resp.embeddings:
                        normalized = [normalize_vector(emb) for emb in resp.embeddings]
                        all_embeddings.extend(normalized)
                        continue
                except Exception as e:
                    logger.warning("Provider embedding failed, falling back to deterministic embedding", error=str(e))

            # Fallback deterministic embeddings
            for t in batch:
                all_embeddings.append(deterministic_mock_embedding(t, self.dimensions))

        return all_embeddings
