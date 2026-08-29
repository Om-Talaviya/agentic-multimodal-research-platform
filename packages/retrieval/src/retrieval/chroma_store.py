"""ChromaDB vector store adapter."""

from typing import Any, Dict, List, Optional
from retrieval.vector_store import SearchResult, VectorDocument, VectorStore
from shared.config import settings
from shared.logging import get_logger

logger = get_logger(__name__)


class ChromaVectorStore(VectorStore):
    """VectorStore implementation backed by ChromaDB."""

    def __init__(
        self,
        collection_name: str = "research_knowledge",
        host: Optional[str] = None,
        port: Optional[int] = None,
        persist_directory: Optional[str] = None,
        client: Optional[Any] = None,
    ) -> None:
        self.collection_name = collection_name
        self.host = host or settings.chroma_host
        self.port = port or settings.chroma_port
        self.persist_directory = persist_directory
        self._client = client
        self._collection = None
        self._initialized = False

    @property
    def is_available(self) -> bool:
        """Check if ChromaDB client library is installed and operational."""
        try:
            import chromadb  # noqa: F401
            return True
        except ImportError:
            return False

    def _get_collection(self) -> Any:
        """Lazy-initialize Chroma collection."""
        if self._collection is not None:
            return self._collection

        if self._client is not None:
            self._collection = self._client.get_or_create_collection(name=self.collection_name)
            self._initialized = True
            return self._collection

        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings

            if self.persist_directory:
                client = chromadb.PersistentClient(path=self.persist_directory)
            else:
                try:
                    client = chromadb.HttpClient(
                        host=self.host,
                        port=self.port,
                        settings=ChromaSettings(anonymized_telemetry=False),
                    )
                    # Verify connectivity
                    client.heartbeat()
                except Exception as net_err:
                    logger.warning("Could not connect to Chroma HTTP, falling back to EphemeralClient", error=str(net_err))
                    client = chromadb.EphemeralClient()

            self._client = client
            self._collection = client.get_or_create_collection(name=self.collection_name)
            self._initialized = True
            return self._collection
        except ImportError:
            raise RuntimeError("chromadb library is not installed. Please use InMemoryVectorStore or install chromadb.")
        except Exception as e:
            logger.error("Failed to initialize Chroma collection", error=str(e))
            raise

    async def add(self, documents: List[VectorDocument]) -> None:
        """Add documents to Chroma collection."""
        if not documents:
            return
        collection = self._get_collection()

        ids = [doc.id for doc in documents]
        embeddings = [doc.embedding for doc in documents]
        documents_text = [doc.content for doc in documents]
        metadatas = [
            {k: str(v) if isinstance(v, (dict, list)) else v for k, v in doc.metadata.items()}
            for doc in documents
        ]

        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents_text,
            metadatas=metadatas,
        )

    async def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search Chroma collection for nearest vectors."""
        collection = self._get_collection()

        where_clause = filter if filter else None
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where=where_clause,
            include=["documents", "metadatas", "distances"],
        )

        search_results: List[SearchResult] = []
        if results and "ids" in results and results["ids"]:
            ids = results["ids"][0]
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            for i, doc_id in enumerate(ids):
                # Convert distance (L2 or cosine distance) to similarity score
                dist = distances[i] if i < len(distances) else 1.0
                score = max(0.0, 1.0 - dist) if dist is not None else 0.5
                doc_text = docs[i] if i < len(docs) else ""
                metadata = metas[i] if i < len(metas) and metas[i] else {}

                search_results.append(
                    SearchResult(
                        id=doc_id,
                        score=score,
                        content=doc_text,
                        metadata=metadata,
                    )
                )

        return search_results

    async def delete(self, ids: List[str]) -> None:
        """Delete documents by ID."""
        if not ids:
            return
        collection = self._get_collection()
        collection.delete(ids=ids)

    async def get(self, id: str) -> Optional[VectorDocument]:
        """Retrieve a vector document from Chroma collection."""
        collection = self._get_collection()
        result = collection.get(ids=[id], include=["documents", "metadatas", "embeddings"])
        if not result or not result["ids"]:
            return None

        content = result["documents"][0] if result.get("documents") else ""
        metadata = result["metadatas"][0] if result.get("metadatas") else {}
        embedding = result["embeddings"][0] if result.get("embeddings") else []

        return VectorDocument(
            id=id,
            content=content,
            embedding=embedding,
            metadata=metadata,
        )

    async def clear(self) -> None:
        """Reset and recreate collection."""
        if self._client is not None:
            try:
                self._client.delete_collection(self.collection_name)
            except Exception:
                pass
            self._collection = None

    async def count(self) -> int:
        """Return total document count in Chroma collection."""
        collection = self._get_collection()
        return collection.count()
