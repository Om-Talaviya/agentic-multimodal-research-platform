"""Research memory tools for agent-level cross-session recall and persistence."""

from typing import Any, Dict, List, Optional
from tools.base import Permission, Tool, ToolParameter, ToolSchema
from shared.logging import get_logger

logger = get_logger(__name__)


class RecallMemoryTool(Tool):
    """Tool to recall past research memories, prior job findings, and conceptual notes."""

    schema = ToolSchema(
        name="recall_memory",
        description="Recall past research memories, prior job findings, methodologies, insights, and concepts stored across user sessions",
        parameters=[
            ToolParameter(
                name="query",
                type="string",
                description="Search query or conceptual topic to recall from memory",
                required=True,
            ),
            ToolParameter(
                name="top_k",
                type="integer",
                description="Maximum number of relevant memories to retrieve",
                required=False,
                default=5,
            ),
            ToolParameter(
                name="memory_type",
                type="string",
                description="Filter by memory type: 'finding', 'insight', 'methodology', 'concept', 'summary', 'hypothesis'",
                required=False,
            ),
            ToolParameter(
                name="tags",
                type="list",
                description="List of specific topic tags to filter by (optional)",
                required=False,
            ),
            ToolParameter(
                name="user_id",
                type="string",
                description="User ID to filter memories for (optional)",
                required=False,
            ),
        ],
        returns="List of recalled memory items matching the query and filters with relevance scores",
        permissions=[Permission.DOCUMENT_ACCESS],
    )

    def __init__(self, memory_manager: Optional[Any] = None) -> None:
        self._memory_manager = memory_manager

    async def execute(
        self,
        query: str,
        top_k: int = 5,
        memory_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        user_id: Optional[str] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """Execute cross-session memory recall."""
        try:
            mem_mgr = self._memory_manager
            if mem_mgr is None:
                from research.memory.manager import ResearchMemoryManager
                mem_mgr = ResearchMemoryManager()

            result = await mem_mgr.recall_memories(
                user_id=user_id,
                query=query,
                top_k=top_k,
                memory_type=memory_type,
                tags=tags,
            )

            return [item.model_dump(mode="json") for item in result.memories]
        except Exception as e:
            logger.error("RecallMemoryTool failed", query=query, error=str(e))
            return []


class StoreMemoryTool(Tool):
    """Tool to persist a new finding, insight, concept, or methodology note into research memory."""

    schema = ToolSchema(
        name="store_memory",
        description="Store a new key finding, concept definition, insight, or methodology note into persistent cross-session research memory",
        parameters=[
            ToolParameter(
                name="title",
                type="string",
                description="Concise, clear title for the memory item",
                required=True,
            ),
            ToolParameter(
                name="content",
                type="string",
                description="Detailed content, finding, or concept definition to remember",
                required=True,
            ),
            ToolParameter(
                name="memory_type",
                type="string",
                description="Type of memory: 'finding', 'insight', 'methodology', 'concept', 'summary', 'hypothesis'",
                required=False,
                default="finding",
            ),
            ToolParameter(
                name="tags",
                type="list",
                description="List of conceptual tags for indexing (e.g. ['quantum', 'qaoa'])",
                required=False,
            ),
            ToolParameter(
                name="confidence",
                type="number",
                description="Confidence score for this finding (0.0 to 1.0)",
                required=False,
                default=1.0,
            ),
            ToolParameter(
                name="user_id",
                type="string",
                description="User ID to own this memory (optional)",
                required=False,
            ),
            ToolParameter(
                name="job_id",
                type="string",
                description="Associated research job ID (optional)",
                required=False,
            ),
        ],
        returns="Object indicating success status and stored memory ID",
        permissions=[Permission.DOCUMENT_ACCESS],
    )

    def __init__(self, memory_manager: Optional[Any] = None) -> None:
        self._memory_manager = memory_manager

    async def execute(
        self,
        title: str,
        content: str,
        memory_type: str = "finding",
        tags: Optional[List[str]] = None,
        confidence: float = 1.0,
        user_id: Optional[str] = None,
        job_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Store item in persistent research memory."""
        try:
            mem_mgr = self._memory_manager
            if mem_mgr is None:
                from research.memory.manager import ResearchMemoryManager
                mem_mgr = ResearchMemoryManager()

            stored = await mem_mgr.store_memory(
                title=title,
                content=content,
                memory_type=memory_type,
                user_id=user_id,
                job_id=job_id,
                tags=tags or [],
                confidence=confidence,
                source_type="agent",
            )

            return {
                "success": True,
                "memory_id": str(stored.id),
                "title": stored.title,
                "memory_type": stored.memory_type.value if hasattr(stored.memory_type, "value") else str(stored.memory_type),
            }
        except Exception as e:
            logger.error("StoreMemoryTool failed", title=title, error=str(e))
            return {
                "success": False,
                "error": str(e),
            }
