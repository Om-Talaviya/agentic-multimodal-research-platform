"""Document upload and management routes."""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_session
from database.repositories import DocumentRepository
from database.models import Document
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
    id: UUID
    filename: str
    mime_type: str
    file_size: int
    file_path: str
    status: str
    created_at: str
    
    class Config:
        from_attributes = True


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
    session: AsyncSession = Depends(get_session),
):
    """Upload a document for research."""
    content = await validate_upload(file)
    file_path, safe_name = await save_upload(content, file.filename, research_job_id)
    
    doc = Document(
        filename=file.filename,
        mime_type=file.content_type or "application/octet-stream",
        file_size=len(content),
        file_path=file_path,
        job_id=UUID(research_job_id) if research_job_id else None,
        status="uploaded",
    )
    
    repo = DocumentRepository(session)
    await repo.create(doc)
    
    logger.info("Document uploaded", doc_id=doc.id, filename=file.filename, job_id=research_job_id)
    
    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        mime_type=doc.mime_type,
        file_size=doc.file_size,
        file_path=doc.file_path,
        status=doc.status,
        created_at=doc.created_at.isoformat(),
    )


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    """Get document by ID."""
    repo = DocumentRepository(session)
    doc = await repo.get(doc_id)
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(
        id=doc.id,
        filename=doc.filename,
        mime_type=doc.mime_type,
        file_size=doc.file_size,
        file_path=doc.file_path,
        status=doc.status,
        created_at=doc.created_at.isoformat(),
    )


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    job_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
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
            file_size=d.file_size,
            file_path=d.file_path,
            status=d.status,
            created_at=d.created_at.isoformat(),
        )
        for d in docs[offset:offset+limit]
    ]