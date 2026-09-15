"""Document and chunk models."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Integer, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class Document(Base):
    """Uploaded/ingested document."""
    
    __tablename__ = "documents"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    workspace_id = Column(GUID(), ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True, index=True)
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    job_id = Column(GUID(), ForeignKey("research_jobs.id", ondelete="SET NULL"), index=True)
    filename = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    content = Column(Text)
    doc_metadata = Column(JSON().with_variant(JSONB, "postgresql"), default=dict)
    file_size = Column(Integer)
    file_path = Column(String(1000))
    status = Column(String(50), default="ready", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    
    # Relationships
    job = relationship("ResearchJob", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan", lazy="dynamic")
    
    __table_args__ = (
        Index("ix_documents_job_created", "job_id", "created_at"),
    )


class DocumentChunk(Base):
    """Document chunk for RAG."""
    
    __tablename__ = "document_chunks"
    
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    document_id = Column(GUID(), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    # embedding = Column(Vector(768))  # Requires pgvector extension
    chunk_metadata = Column(JSON().with_variant(JSONB, "postgresql"), default=dict)
    chunk_index = Column(Integer, nullable=False)
    start_char = Column(Integer)
    end_char = Column(Integer)
    
    # Relationships
    document = relationship("Document", back_populates="chunks")
    
    __table_args__ = (
        Index("ix_document_chunks_doc_index", "document_id", "chunk_index"),
    )
