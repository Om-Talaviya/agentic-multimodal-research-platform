"""Document upload and management routes."""

import io
from pathlib import Path
from datetime import UTC, datetime
from typing import Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session
from database.repositories import DocumentRepository
from database.models import Document
from ingestion.pipeline import IngestionPipeline
from ingestion.parsers.registry import ParserRegistry
from ingestion.chunking import SemanticChunker
from ai.gateway.model_gateway import ModelGateway
from shared.config import settings
from shared.logging import get_logger
from shared.exceptions import ValidationError

router = APIRouter(prefix="/documents", tags=["documents"])
logger = get_logger(__name__)


ALLOWED_MIME_TYPES = {
    "text/plain",
    "text/markdown",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "image/png",
    "image/jpeg",
    "image/webp",
}

ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx", ".png", ".jpg", ".jpeg", ".webp"}


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    mime_type: str
    file_size: int
    file_path: str
    status: str = "ingested"
    created_at: str


def utc_now() -> datetime:
    return datetime.now(UTC)


async def get_model_gateway() -> Optional[ModelGateway]:
    """Dependency helper to get active ModelGateway instance."""
    from api.dependencies import get_model_gateway as get_gateway
    try:
        return await get_gateway()
    except Exception:
        return None


async def get_knowledge_indexer():
    """Dependency helper to get active KnowledgeIndexer instance."""
    from api.dependencies import get_indexer
    try:
        return await get_indexer()
    except Exception:
        return None


async def get_knowledge_retriever():
    """Dependency helper to get active HybridRetriever instance."""
    from api.dependencies import get_retriever
    try:
        return await get_retriever()
    except Exception:
        return None


async def validate_upload(file: UploadFile) -> bytes:
    """Validate uploaded file."""
    content = await file.read()
    
    # Check file size
    if len(content) > settings.max_upload_size:
        raise ValidationError(
            f"File too large (max {settings.max_upload_size} bytes)",
            details={"max_size": settings.max_upload_size, "actual_size": len(content)},
        )
    
    # Check extension
    from pathlib import Path
    raw_filename = file.filename or "unnamed_document"
    ext = Path(raw_filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"File type not allowed: {ext}",
            details={"allowed_extensions": list(ALLOWED_EXTENSIONS)},
        )
    
    # Check MIME type (basic check)
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise ValidationError(
            f"Invalid file content type: {file.content_type}",
            details={"allowed_types": list(ALLOWED_MIME_TYPES)},
        )
    
    return content


async def save_upload(content: bytes, filename: str, job_id: Optional[str] = None) -> tuple[str, str]:
    """Save upload to disk safely preventing path traversal."""
    from pathlib import Path
    import uuid
    
    if job_id:
        try:
            subdir = str(UUID(str(job_id)))
        except (ValueError, TypeError):
            subdir = "".join(c for c in str(job_id) if c.isalnum() or c in "-_") or "unassigned"
    else:
        subdir = "unassigned"

    upload_dir = (settings.upload_dir / subdir).resolve()
    base_dir = settings.upload_dir.resolve()
    
    # Ensure resolved upload directory does not escape root upload directory
    if not str(upload_dir).startswith(str(base_dir)):
        upload_dir = (base_dir / "unassigned").resolve()

    upload_dir.mkdir(parents=True, exist_ok=True)
    
    raw_ext = Path(filename or "doc").suffix.lower()
    if raw_ext not in ALLOWED_EXTENSIONS:
        raw_ext = ".bin"

    safe_name = f"{uuid.uuid4()}{raw_ext}"
    file_path = upload_dir / safe_name
    
    file_path.write_bytes(content)
    
    return str(file_path), safe_name


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    research_job_id: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_db_session),
    gateway: Optional[ModelGateway] = Depends(get_model_gateway),
    indexer: Optional[Any] = Depends(get_knowledge_indexer),
):
    """Upload a document, parse chunks, persist, and automatically index into the knowledge base."""
    content = await validate_upload(file)
    file_path, safe_name = await save_upload(content, file.filename, research_job_id)
    
    repo = DocumentRepository(session)
    parser_registry = ParserRegistry(vision_source=gateway)
    pipeline = IngestionPipeline(
        parser_registry=parser_registry,
        chunker=SemanticChunker(),
        doc_repo=repo,
        indexer=indexer,
    )
    
    doc_id: Optional[UUID] = None
    file_io = io.BytesIO(content)
    try:
        result = await pipeline.ingest(
            file=file_io,
            filename=file.filename,
            mime_type=file.content_type,
            research_job_id=research_job_id,
            file_path=file_path,
        )
        doc_id = UUID(result.document_id)
        logger.info(
            "Document uploaded and ingested with knowledge auto-indexing",
            doc_id=result.document_id,
            filename=file.filename,
            chunks=len(result.chunks),
            indexed_chunks=result.indexed_chunk_count,
            tables=result.table_count,
            images=result.image_count,
        )
    except Exception as e:
        logger.error("Ingestion failed during document upload, falling back to raw record", filename=file.filename, error=str(e))
        doc = Document(
            filename=file.filename,
            mime_type=file.content_type or "application/octet-stream",
            file_size=len(content),
            file_path=file_path,
            job_id=UUID(research_job_id) if research_job_id else None,
            content="",
            status="failed",
            doc_metadata={"ingestion_error": str(e)},
            created_at=utc_now(),
        )
        await repo.create(doc)
        doc_id = doc.id
    
    doc = await repo.get(doc_id)
    if not doc:
        raise HTTPException(status_code=500, detail="Failed to retrieve uploaded document")
    
    created_str = doc.created_at.isoformat() if doc.created_at else utc_now().isoformat()
    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        mime_type=doc.mime_type,
        file_size=doc.file_size or len(content),
        file_path=doc.file_path or file_path,
        status=getattr(doc, "status", "ready"),
        created_at=created_str,
    )


@router.get("/search", response_model=list[dict])
async def search_knowledge_base(
    q: str,
    top_k: int = 5,
    document_id: Optional[str] = None,
    modality: Optional[str] = None,
    retriever: Optional[Any] = Depends(get_knowledge_retriever),
):
    """Search indexed knowledge base documents using hybrid RAG (dense vector + sparse BM25 + RRF)."""
    if not retriever:
        raise HTTPException(status_code=503, detail="Retrieval engine is not initialized")
    
    filter_dict = {}
    if document_id:
        filter_dict["document_id"] = str(document_id)
    if modality:
        filter_dict["modality"] = modality

    results = await retriever.retrieve(
        query=q,
        top_k=top_k,
        filter=filter_dict if filter_dict else None,
    )
    return [ev.to_dict() for ev in results]


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Get document by ID."""
    repo = DocumentRepository(session)
    doc = await repo.get(doc_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    created_str = doc.created_at.isoformat() if doc.created_at else utc_now().isoformat()
    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        mime_type=doc.mime_type,
        file_size=doc.file_size or 0,
        file_path=doc.file_path or "",
        status=getattr(doc, "status", "ready"),
        created_at=created_str,
    )


@router.post("/{doc_id}/reindex")
async def reindex_document(
    doc_id: UUID,
    indexer: Optional[Any] = Depends(get_knowledge_indexer),
):
    """Reindex an existing document and its chunks into the knowledge base."""
    if not indexer:
        raise HTTPException(status_code=503, detail="Knowledge indexer is not initialized")
    
    indexed_count = await indexer.index_document_by_id(doc_id)
    if indexed_count == 0:
        raise HTTPException(status_code=404, detail="Document not found or has no indexable content")
    
    return {
        "status": "reindexed",
        "document_id": str(doc_id),
        "indexed_chunks": indexed_count,
    }


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    doc_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    indexer: Optional[Any] = Depends(get_knowledge_indexer),
):
    """Delete a document, its chunks from DB, physical file from disk, and vector/BM25 indices."""
    from pathlib import Path
    repo = DocumentRepository(session)
    doc = await repo.get(doc_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # 1. Delete from indices
    if indexer:
        try:
            await indexer.delete_document(doc_id)
        except Exception as idx_err:
            logger.warning("Error removing document from indices during delete", error=str(idx_err))

    # 2. Delete physical file
    if doc.file_path:
        try:
            p = Path(doc.file_path)
            if p.exists():
                p.unlink(missing_ok=True)
        except Exception as f_err:
            logger.warning("Error removing physical file during delete", error=str(f_err))

    # 3. Delete from DB
    await repo.delete(doc_id)
    return None


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    job_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session),
):
    """List documents with optional job_id filtering and pagination."""
    repo = DocumentRepository(session)
    
    if job_id:
        try:
            parsed_job_id = UUID(str(job_id))
            docs = await repo.get_by_job(parsed_job_id)
            docs = docs[offset:offset + limit]
        except (ValueError, TypeError):
            docs = []
    else:
        docs = await repo.list_all(limit=limit, offset=offset)
    
    return [
        DocumentResponse(
            id=d.id,
            filename=d.filename,
            mime_type=d.mime_type,
            file_size=d.file_size or 0,
            file_path=d.file_path or "",
            status=getattr(d, "status", "ready"),
            created_at=d.created_at.isoformat() if d.created_at else utc_now().isoformat(),
        )
        for d in docs
    ]
