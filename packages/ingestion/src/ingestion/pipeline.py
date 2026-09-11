"""Ingestion pipeline orchestrating document parsing, normalization, chunking, and persistence."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, BinaryIO, Dict, List, Optional
from uuid import UUID, uuid4
from ingestion.chunking import Chunk, ChunkingStrategy, SemanticChunker
from ingestion.parsers.base import ParsedDocument
from ingestion.parsers.registry import ParserRegistry
from shared.logging import get_logger

logger = get_logger(__name__)


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass
class IngestionResult:
    """Result of running a document through the ingestion pipeline."""

    document_id: str
    filename: str
    parsed_document: ParsedDocument
    chunks: List[Chunk]
    table_count: int
    image_count: int
    status: str = "ready"
    indexed_chunk_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class IngestionPipeline:
    """Orchestrates end-to-end ingestion: parse -> extract -> chunk -> persist -> index."""

    def __init__(
        self,
        parser_registry: Optional[ParserRegistry] = None,
        chunker: Optional[ChunkingStrategy] = None,
        doc_repo: Optional[Any] = None,
        indexer: Optional[Any] = None,
    ) -> None:
        self.parser_registry = parser_registry or ParserRegistry()
        self.chunker = chunker or SemanticChunker()
        self.doc_repo = doc_repo
        self.indexer = indexer

    async def ingest(
        self,
        file: BinaryIO,
        filename: str,
        mime_type: Optional[str] = None,
        research_job_id: Optional[str] = None,
        document_id: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> IngestionResult:
        """Run a document through format detection, parsing, chunking, database persistence, and vector/BM25 indexing."""
        doc_id = document_id or str(uuid4())
        logger.info("Starting ingestion pipeline for document", filename=filename, doc_id=doc_id)

        # 1. Parse document
        parsed = await self.parser_registry.parse(file, filename, mime_type)

        # 2. Chunk parsed content
        chunks = self.chunker.chunk(parsed)

        chunk_models = []
        doc_status = "ready"

        # 3. Persist to repository if available
        if self.doc_repo is not None:
            try:
                from database.models import Document, DocumentChunk

                job_uuid = UUID(research_job_id) if research_job_id else None
                doc_model = Document(
                    id=UUID(doc_id) if isinstance(doc_id, str) else doc_id,
                    job_id=job_uuid,
                    filename=filename,
                    mime_type=mime_type or parsed.metadata.get("mime_type", "application/octet-stream"),
                    content=parsed.content,
                    doc_metadata=parsed.metadata,
                    file_size=parsed.metadata.get("byte_size", len(parsed.content.encode("utf-8"))),
                    file_path=file_path,
                    status="processing",
                    created_at=utc_now(),
                )
                await self.doc_repo.create(doc_model)

                for i, c in enumerate(chunks):
                    chunk_model = DocumentChunk(
                        id=uuid4(),
                        document_id=doc_model.id,
                        content=c.content,
                        chunk_metadata=c.metadata,
                        chunk_index=i,
                        start_char=c.start_char,
                        end_char=c.end_char,
                    )
                    chunk_models.append(chunk_model)

                if chunk_models:
                    await self.doc_repo.create_chunks(chunk_models)

                logger.info(
                    "Persisted document and chunks to database",
                    doc_id=doc_id,
                    chunks=len(chunk_models),
                )
            except Exception as db_err:
                logger.warning("Failed to persist document to repository", error=str(db_err))
                doc_status = "error_persisting"

        # 4. Auto-index chunks into VectorStore & BM25 index if indexer is available
        indexed_count = 0
        if self.indexer is not None and chunks:
            try:
                indexed_items = []
                for i, c in enumerate(chunks):
                    indexed_items.append({
                        "id": str(chunk_models[i].id) if i < len(chunk_models) else str(uuid4()),
                        "document_id": str(doc_id),
                        "content": c.content,
                        "metadata": {
                            **c.metadata,
                            "filename": filename,
                            "document_id": str(doc_id),
                            "chunk_index": i,
                        },
                        "chunk_index": i,
                        "start_char": c.start_char,
                        "end_char": c.end_char,
                    })

                indexed_count = await self.indexer.index_chunks(
                    chunks=indexed_items,
                    document_id=str(doc_id),
                    filename=filename,
                )
                logger.info(
                    "Auto-indexed document chunks into knowledge base",
                    doc_id=doc_id,
                    indexed_chunks=indexed_count,
                )
            except Exception as index_err:
                logger.warning("Failed to auto-index document chunks", doc_id=doc_id, error=str(index_err))
                doc_status = "error_indexing"

        # 5. Finalize document status in DB
        if self.doc_repo is not None and hasattr(self.doc_repo, "update_status"):
            try:
                final_status = "ready" if doc_status not in ("error_persisting", "error_indexing") else doc_status
                await self.doc_repo.update_status(
                    doc_id=UUID(doc_id) if isinstance(doc_id, str) else doc_id,
                    status=final_status,
                )
            except Exception as status_err:
                logger.warning("Failed to update final document status", error=str(status_err))

        result = IngestionResult(
            document_id=doc_id,
            filename=filename,
            parsed_document=parsed,
            chunks=chunks,
            table_count=len(parsed.tables),
            image_count=len(parsed.images),
            status="ready" if doc_status not in ("error_persisting", "error_indexing") else doc_status,
            indexed_chunk_count=indexed_count,
            metadata={
                "research_job_id": research_job_id,
                "char_count": len(parsed.content),
                "chunk_count": len(chunks),
                "indexed_chunks": indexed_count,
                **parsed.metadata,
            },
        )

        logger.info(
            "Ingestion completed successfully",
            filename=filename,
            doc_id=doc_id,
            chunks=len(chunks),
            tables=len(parsed.tables),
            images=len(parsed.images),
            indexed_chunks=indexed_count,
        )
        return result
