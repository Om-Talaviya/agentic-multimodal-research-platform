"""Vector store abstraction and data models."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class VectorDocument:
    """Document or chunk with vector embedding and metadata."""

    id: str
    content: str
    embedding: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """Search result from dense or sparse retrieval."""

    id: str
    score: float
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "score": self.score,
            "content": self.content,
            "metadata": self.metadata,
        }


class VectorStore(ABC):
    """Abstract base class for vector store backends."""

    @abstractmethod
    async def add(self, documents: List[VectorDocument]) -> None:
        """Add or update vector documents in the store."""
        pass

    @abstractmethod
    async def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search for top_k nearest neighbors given a query embedding."""
        pass

    @abstractmethod
    async def delete(self, ids: List[str]) -> None:
        """Delete documents by their IDs."""
        pass

    @abstractmethod
    async def get(self, id: str) -> Optional[VectorDocument]:
        """Retrieve a vector document by its ID."""
        pass

    @abstractmethod
    async def clear(self) -> None:
        """Clear all documents from the store."""
        pass

    @abstractmethod
    async def count(self) -> int:
        """Return the number of documents in the store."""
        pass
