"""Document read tool definition supporting multimodal chunks, tables, and vision metadata."""

from uuid import UUID
from tools.base import Tool, ToolSchema, ToolParameter, Permission
from shared.logging import get_logger

logger = get_logger(__name__)


class DocumentReadTool(Tool):
    """Read content, chunks, tables, and visual metadata from an uploaded document."""

    schema = ToolSchema(
        name="document_read",
        description="Read content, chunks, tables, or metadata from an uploaded document by ID",
        parameters=[
            ToolParameter(
                name="document_id",
                type="string",
                description="Document ID",
                required=True,
            ),
            ToolParameter(
                name="section",
                type="string",
                description="Section or keyword to filter chunks (optional)",
                required=False,
            ),
            ToolParameter(
                name="chunk_index",
                type="integer",
                description="Specific chunk index to read (optional)",
                required=False,
            ),
        ],
        returns="Document content, structured chunks, or table/image metadata",
        permissions=[Permission.DOCUMENT_ACCESS],
    )

    async def execute(
        self,
        document_id: str,
        section: str | None = None,
        chunk_index: int | None = None,
    ) -> str:
        # Lazy import to avoid circular dependency
        from database.repositories import DocumentRepository
        from database.connection import get_session

        try:
            doc_uuid = UUID(document_id) if isinstance(document_id, str) else document_id
            async with get_session() as session:
                doc_repo = DocumentRepository(session)
                doc = await doc_repo.get_with_chunks(doc_uuid)

                if not doc:
                    return f"Document not found: {document_id}"

                chunks = list(doc.chunks) if doc.chunks else []

                # Return specific chunk if requested
                if chunk_index is not None:
                    if 0 <= chunk_index < len(chunks):
                        c = chunks[chunk_index]
                        return f"--- Chunk {chunk_index} ---\n{c.content}"
                    return f"Chunk index {chunk_index} out of range (total {len(chunks)} chunks)"

                # Filter by section if requested
                if section:
                    matching_chunks = [
                        c for c in chunks
                        if section.lower() in (c.content or "").lower()[:300]
                        or section.lower() in str(c.chunk_metadata or {}).lower()
                    ]
                    if matching_chunks:
                        return "\n\n---\n\n".join(
                            f"--- Chunk {c.chunk_index} ---\n{c.content}"
                            for c in matching_chunks[:5]
                        )
                    # If full text contains section
                    if doc.content and section.lower() in doc.content.lower():
                        idx = doc.content.lower().find(section.lower())
                        start = max(0, idx - 100)
                        end = min(len(doc.content), idx + 2000)
                        return doc.content[start:end]
                    return f"Section '{section}' not found in document"

                # If structured chunks exist, format rich text
                if chunks:
                    output_parts = [f"=== Document: {doc.filename} (Chunks: {len(chunks)}) ==="]
                    for c in chunks[:15]:
                        meta_info = f" [Type: {c.chunk_metadata.get('type')}]" if c.chunk_metadata and 'type' in c.chunk_metadata else ""
                        output_parts.append(f"--- Chunk {c.chunk_index}{meta_info} ---\n{c.content}")
                    return "\n\n".join(output_parts)[:50000]

                # Fallback to full raw content
                if doc.content:
                    return doc.content[:50000]

                return f"Document {doc.filename} has no readable content"

        except Exception as e:
            logger.error("Document read failed", document_id=document_id, error=str(e))
            return f"Error reading document: {str(e)}"