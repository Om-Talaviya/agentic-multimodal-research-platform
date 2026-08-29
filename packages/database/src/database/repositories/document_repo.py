"""Document repository."""

from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from database.models import Document, DocumentChunk


class DocumentRepository:
    """Repository for document operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, document: Document) -> Document:
        self.session.add(document)
        await self.session.flush()
        return document
    
    async def get(self, doc_id: UUID) -> Optional[Document]:
        result = await self.session.execute(
            select(Document).where(Document.id == doc_id)
        )
        return result.scalar_one_or_none()
    
    async def get_with_chunks(self, doc_id: UUID) -> Optional[Document]:
        result = await self.session.execute(
            select(Document)
            .options(selectinload(Document.chunks))
            .where(Document.id == doc_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_job(self, job_id: UUID) -> List[Document]:
        result = await self.session.execute(
            select(Document).where(Document.job_id == job_id)
        )
        return list(result.scalars().all())
    
    async def create_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        self.session.add_all(chunks)
        await self.session.flush()
        return chunks


class DocumentChunkRepository:
    """Repository for document chunk operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, chunk: DocumentChunk) -> DocumentChunk:
        self.session.add(chunk)
        await self.session.flush()
        return chunk
    
    async def create_batch(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        self.session.add_all(chunks)
        await self.session.flush()
        return chunks
    
    async def get_by_document(self, doc_id: UUID) -> List[DocumentChunk]:
        result = await self.session.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == doc_id)
            .order_by(DocumentChunk.chunk_index)
        )
        return list(result.scalars().all())