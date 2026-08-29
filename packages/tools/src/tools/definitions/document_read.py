"""Document read tool definition."""

from tools.base import Tool, ToolSchema, ToolParameter, Permission
from shared.logging import get_logger

logger = get_logger(__name__)


class DocumentReadTool(Tool):
    """Read content from an uploaded document."""
    
    schema = ToolSchema(
        name="document_read",
        description="Read content from an uploaded document by ID",
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
                description="Section to read (optional)",
                required=False,
            ),
        ],
        returns="Document content",
        permissions=[Permission.DOCUMENT_ACCESS],
    )
    
    async def execute(self, document_id: str, section: str | None = None) -> str:
        # Lazy import to avoid circular dependency
        from database.repositories import DocumentRepository
        from database.connection import get_session
        
        try:
            async with get_session() as session:
                doc_repo = DocumentRepository(session)
                doc = await doc_repo.get_with_chunks(document_id)
                
                if not doc:
                    return f"Document not found: {document_id}"
                
                if section:
                    # Find chunk matching section
                    for chunk in doc.chunks:
                        if section.lower() in chunk.content.lower()[:200]:
                            return chunk.content
                    return f"Section '{section}' not found in document"
                
                # Return full content or first few chunks
                if doc.content:
                    return doc.content[:50000]
                
                # Fallback to chunks
                chunks_text = "\n\n---\n\n".join(c.content for c in doc.chunks[:10])
                return chunks_text[:50000]
                
        except Exception as e:
            logger.error("Document read failed", document_id=document_id, error=str(e))
            return f"Error reading document: {str(e)}"