"""Document upload and management routes."""

import io
from datetime import UTC, datetime
from typing import Optional
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
    ext = Path(file.filename).suffix.lower()
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
    """Save upload to disk."""
    from pathlib import Path
    import uuid
    
    subdir = job_id or "unassigned"
    upload_dir = settings.upload_dir / subdir
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    safe_name = f"{uuid.uuid4()}{Path(filename).suffix}"
    file_path = upload_dir / safe_name
    
    file_path.write_bytes(content)
    
    return str(file_path), safe_name


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    research_job_id: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_db_session),
    gateway: Optional[ModelGateway] = Depends(get_model_gateway),
):
    """Upload a document and run it through the multimodal ingestion pipeline."""
    content = await validate_upload(file)
    file_path, safe_name = await save_upload(content, file.filename, research_job_id)
    
    repo = DocumentRepository(session)
    parser_registry = ParserRegistry(vision_source=gateway)
    pipeline = IngestionPipeline(
        parser_registry=parser_registry,
        chunker=SemanticChunker(),
        doc_repo=repo,
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
            "Document uploaded and ingested",
            doc_id=result.document_id,
            filename=file.filename,
            chunks=len(result.chunks),
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
        status="ingested",
        created_at=created_str,
    )


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
        status="ingested",
        created_at=created_str,
    )


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    job_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    session: AsyncSession = Depends(get_db_session),
):
    """List documents."""
    repo = DocumentRepository(session)
    
    if job_id:
        docs = await repo.get_by_job(UUID(job_id))
    else:
        # For now, return empty list if no job_id
        docs = []
    
    return [
        DocumentResponse(
            id=d.id,
            filename=d.filename,
            mime_type=d.mime_type,
            file_size=d.file_size or 0,
            file_path=d.file_path or "",
            status="ingested",
            created_at=d.created_at.isoformat() if d.created_at else utc_now().isoformat(),
        )
        for d in docs[offset:offset+limit]
    ]
