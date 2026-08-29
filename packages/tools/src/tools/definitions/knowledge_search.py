"""Knowledge search tool for semantic and hybrid retrieval over indexed documents."""

from typing import Any, Dict, List, Optional
from tools.base import Permission, Tool, ToolParameter, ToolSchema
from shared.logging import get_logger

logger = get_logger(__name__)


class KnowledgeSearchTool(Tool):
    """Semantic and hybrid search tool over indexed document chunks."""

    schema = ToolSchema(
        name="knowledge_search",
        description="Search indexed knowledge base documents, tables, and visual annotations using hybrid RAG retrieval",
        parameters=[
            ToolParameter(
                name="query",
                type="string",
                description="Search query or question",
                required=True,
            ),
            ToolParameter(
                name="top_k",
                type="integer",
                description="Number of results to return",
                required=False,
                default=5,
            ),
            ToolParameter(
                name="document_id",
                type="string",
                description="Filter search by specific document ID (optional)",
                required=False,
            ),
            ToolParameter(
                name="modality",
                type="string",
                description="Filter by modality: 'text', 'table', or 'image' (optional)",
                required=False,
            ),
        ],
        returns="List of grounded evidence passages with similarity scores and citations",
        permissions=[Permission.DOCUMENT_ACCESS],
    )

    def __init__(self, retriever: Optional[Any] = None) -> None:
        self._retriever = retriever

    async def execute(
        self,
        query: str,
        top_k: int = 5,
        document_id: Optional[str] = None,
        modality: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Execute hybrid search query."""
        retriever = self._retriever
        if retriever is None:
            # Try to obtain global/dependency retriever
            try:
                from api.dependencies import get_retriever
                retriever = await get_retriever()
            except Exception:
                # Fallback to local in-memory retriever instance
                from retrieval.bm25 import BM25Index
                from retrieval.embedder import Embedder
                from retrieval.in_memory_store import InMemoryVectorStore
                from retrieval.retriever import HybridRetriever

                retriever = HybridRetriever(
                    vector_store=InMemoryVectorStore(),
                    bm25_index=BM25Index(),
                    embedder=Embedder(),
                )

        # Build filter
        filter_dict: Dict[str, Any] = {}
        if document_id:
            filter_dict["document_id"] = str(document_id)
        if modality:
            filter_dict["modality"] = modality

        try:
            evidence_results = await retriever.retrieve(
                query=query,
                top_k=top_k,
                filter=filter_dict if filter_dict else None,
            )

            return [ev.to_dict() for ev in evidence_results]
        except Exception as e:
            logger.error("Knowledge search failed", query=query, error=str(e))
            return []
