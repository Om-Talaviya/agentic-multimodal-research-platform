"""In-memory vector store with cosine similarity, metadata filtering, and persistence."""

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional
from retrieval.vector_store import SearchResult, VectorDocument, VectorStore
from shared.logging import get_logger

logger = get_logger(__name__)


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0

    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))

    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0

    return dot_product / (norm1 * norm2)


class InMemoryVectorStore(VectorStore):
    """In-memory vector store implementing cosine similarity search."""

    def __init__(self, persist_path: Optional[str | Path] = None) -> None:
        self._docs: Dict[str, VectorDocument] = {}
        self._persist_path = Path(persist_path) if persist_path else None
        if self._persist_path and self._persist_path.exists():
            self.load(self._persist_path)

    async def add(self, documents: List[VectorDocument]) -> None:
        """Add or update vector documents."""
        for doc in documents:
            self._docs[doc.id] = doc
        if self._persist_path:
            self.save(self._persist_path)

    async def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search for top_k most similar documents."""
        if not self._docs or not query_vector:
            return []

        scored_docs: List[tuple[float, str, VectorDocument]] = []

        for doc_id, doc in self._docs.items():
            # Check metadata filter
            if filter:
                match = True
                for k, v in filter.items():
                    if doc.metadata.get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            score = cosine_similarity(query_vector, doc.embedding)
            # Tuple: (-score, doc_id, doc) for highest score first, stable tie-break
            scored_docs.append((score, doc_id, doc))

        # Sort descending by score, ascending by doc_id
        scored_docs.sort(key=lambda x: (-x[0], x[1]))

        results = []
        for score, _, doc in scored_docs[:top_k]:
            results.append(
                SearchResult(
                    id=doc.id,
                    score=float(score),
                    content=doc.content,
                    metadata=dict(doc.metadata),
                    embedding=list(doc.embedding),
                )
            )

        return results

    async def delete(self, ids: List[str]) -> None:
        """Delete documents by ID."""
        for doc_id in ids:
            self._docs.pop(doc_id, None)
        if self._persist_path:
            self.save(self._persist_path)

    async def get(self, id: str) -> Optional[VectorDocument]:
        """Get document by ID."""
        return self._docs.get(id)

    async def clear(self) -> None:
        """Clear all stored vectors."""
        self._docs.clear()
        if self._persist_path and self._persist_path.exists():
            self._persist_path.unlink(missing_ok=True)

    async def count(self) -> int:
        """Return total document count."""
        return len(self._docs)

    def save(self, path: Path) -> None:
        """Serialize store to a JSON file."""
        data = {
            doc_id: {
                "id": doc.id,
                "content": doc.content,
                "embedding": doc.embedding,
                "metadata": doc.metadata,
            }
            for doc_id, doc in self._docs.items()
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self, path: Path) -> None:
        """Load store from a JSON file."""
        if not path.exists():
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._docs = {
            doc_id: VectorDocument(
                id=item["id"],
                content=item["content"],
                embedding=item["embedding"],
                metadata=item.get("metadata", {}),
            )
            for doc_id, item in data.items()
        }
