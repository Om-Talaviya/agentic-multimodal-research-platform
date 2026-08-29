"""Knowledge indexing pipeline connecting DocumentChunk repositories to vector and lexical indices."""

from typing import Any, Dict, List, Optional
from uuid import UUID
from retrieval.bm25 import BM25Index
from retrieval.embedder import Embedder
from retrieval.vector_store import VectorDocument, VectorStore
from shared.logging import get_logger

logger = get_logger(__name__)


class KnowledgeIndexer:
    """Indexes Document and DocumentChunk database entities into VectorStore and BM25 index."""

    def __init__(
        self,
        vector_store: VectorStore,
        bm25_index: BM25Index,
        embedder: Embedder,
    ) -> None:
        self.vector_store = vector_store
        self.bm25_index = bm25_index
        self.embedder = embedder

    async def index_chunks(
        self,
        chunks: List[Any],
        document_id: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> int:
        """Index a batch of DocumentChunk entities or chunk dictionaries."""
        if not chunks:
            return 0

        texts_to_embed: List[str] = []
        parsed_items: List[Dict[str, Any]] = []

        for c in chunks:
            if isinstance(c, dict):
                chunk_id = str(c.get("id"))
                doc_id = str(c.get("document_id") or document_id or "")
                content = c.get("content", "")
                metadata = dict(c.get("chunk_metadata", {}) or c.get("metadata", {}))
                chunk_idx = c.get("chunk_index")
                start_char = c.get("start_char")
                end_char = c.get("end_char")
            else:
                chunk_id = str(getattr(c, "id", ""))
                doc_id = str(getattr(c, "document_id", document_id or ""))
                content = getattr(c, "content", "")
                metadata = dict(getattr(c, "chunk_metadata", {}) or {})
                chunk_idx = getattr(c, "chunk_index", None)
                start_char = getattr(c, "start_char", None)
                end_char = getattr(c, "end_char", None)

            # Multimodal enhancement
            modality = metadata.get("type", "text")
            if "table_markdown" in metadata:
                modality = "table"
            elif "image" in str(modality) or "vision" in metadata:
                modality = "image"

            metadata["document_id"] = doc_id
            metadata["chunk_id"] = chunk_id
            metadata["chunk_index"] = chunk_idx
            metadata["start_char"] = start_char
            metadata["end_char"] = end_char
            metadata["modality"] = modality
            if filename:
                metadata["filename"] = filename

            texts_to_embed.append(content)
            parsed_items.append({
                "id": chunk_id,
                "content": content,
                "metadata": metadata,
            })

        # Generate batch embeddings
        embeddings = await self.embedder.embed_batch(texts_to_embed)

        # Prepare vector documents
        vector_docs: List[VectorDocument] = []
        for item, emb in zip(parsed_items, embeddings):
            vector_docs.append(
                VectorDocument(
                    id=item["id"],
                    content=item["content"],
                    embedding=emb,
                    metadata=item["metadata"],
                )
            )

        # 1. Add to VectorStore
        await self.vector_store.add(vector_docs)

        # 2. Add to BM25 index
        for item in parsed_items:
            self.bm25_index.add(
                id=item["id"],
                text=item["content"],
                metadata=item["metadata"],
            )

        logger.info(
            "Indexed document chunks successfully",
            chunk_count=len(parsed_items),
            document_id=document_id,
        )
        return len(parsed_items)

    async def index_document_by_id(self, document_id: str | UUID) -> int:
        """Fetch document with its chunks from database and index them."""
        from database.connection import get_session
        from database.repositories import DocumentRepository

        doc_uuid = UUID(str(document_id))
        async with get_session() as session:
            doc_repo = DocumentRepository(session)
            doc = await doc_repo.get_with_chunks(doc_uuid)

            if not doc:
                logger.warning("Document not found for indexing", doc_id=str(document_id))
                return 0

            chunks = list(doc.chunks) if doc.chunks else []
            if not chunks and doc.content:
                # If single content document without explicit chunks
                dummy_chunk = {
                    "id": str(doc.id),
                    "document_id": str(doc.id),
                    "content": doc.content,
                    "chunk_metadata": doc.doc_metadata or {},
                    "chunk_index": 0,
                }
                return await self.index_chunks([dummy_chunk], document_id=str(doc.id), filename=doc.filename)

            return await self.index_chunks(chunks, document_id=str(doc.id), filename=doc.filename)

    async def delete_document(self, document_id: str | UUID) -> None:
        """Delete all chunks for a document from vector and lexical indices."""
        doc_str = str(document_id)
        # 1. Vector store deletion
        try:
            # Query all vectors with document_id and delete
            from database.connection import get_session
            from database.repositories import DocumentChunkRepository

            doc_uuid = UUID(doc_str)
            async with get_session() as session:
                chunk_repo = DocumentChunkRepository(session)
                chunks = await chunk_repo.get_by_document(doc_uuid)
                chunk_ids = [str(c.id) for c in chunks]
                if chunk_ids:
                    await self.vector_store.delete(chunk_ids)
                    self.bm25_index.delete(chunk_ids)
        except Exception as e:
            logger.warning("Error deleting document from indices", document_id=doc_str, error=str(e))
