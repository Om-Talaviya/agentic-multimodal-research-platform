from typing import TYPE_CHECKING, Any, Dict, List, Optional
from tools.base import Tool, ToolParameter, ToolSchema
from database.connection import get_session
from database.repositories.graph_repo import KnowledgeGraphRepository
from shared.logging import get_logger

if TYPE_CHECKING:
    from research.graph.engine import KnowledgeGraphEngine

logger = get_logger(__name__)


class QueryKnowledgeGraphTool(Tool):
    """Tool for querying knowledge graph entities and relations."""

    schema = ToolSchema(
        name="query_knowledge_graph",
        description="Query the research knowledge graph for entities, concepts, and relational subgraphs.",
        parameters=[
            ToolParameter(
                name="query",
                type="string",
                description="Entity name, keyword, or concept to query in the knowledge graph.",
                required=True,
            ),
            ToolParameter(
                name="entity_type",
                type="string",
                description="Optional filter by entity type (CONCEPT, TECHNOLOGY, MATERIAL, PERSON, ORGANIZATION, METRIC, DATASET, PAPER).",
                required=False,
            ),
            ToolParameter(
                name="max_hops",
                type="integer",
                description="Maximum graph hops to traverse for context (1 or 2, default 1).",
                required=False,
                default=1,
            ),
        ],
    )

    def __init__(
        self,
        repo: Optional[KnowledgeGraphRepository] = None,
        graph_engine: Optional[Any] = None,
    ) -> None:
        self._repo = repo
        self._engine = graph_engine

    async def execute(
        self,
        query: str,
        entity_type: Optional[str] = None,
        max_hops: int = 1,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute knowledge graph query."""
        user_id = kwargs.get("user_id")

        if self._engine:
            context_text, subgraphs = await self._engine.get_graph_augmented_context(
                query=query, user_id=user_id, max_hops=max_hops
            )
            entities = []
            if self._repo:
                entities = await self._repo.list_entities(
                    user_id=user_id, entity_type=entity_type, search=query, limit=10
                )
            return {
                "success": True,
                "query": query,
                "context": context_text,
                "entities_found": [e.to_dict() if hasattr(e, "to_dict") else str(e) for e in entities],
                "subgraphs": subgraphs,
                "count": len(entities),
            }

        if self._repo:
            from research.graph.engine import KnowledgeGraphEngine
            engine = KnowledgeGraphEngine(self._repo)
            context_text, subgraphs = await engine.get_graph_augmented_context(
                query=query, user_id=user_id, max_hops=max_hops
            )
            entities = await self._repo.list_entities(
                user_id=user_id, entity_type=entity_type, search=query, limit=10
            )
            return {
                "success": True,
                "query": query,
                "context": context_text,
                "entities_found": [e.to_dict() for e in entities],
                "subgraphs": subgraphs,
                "count": len(entities),
            }

        async with get_session() as session:
            from research.graph.engine import KnowledgeGraphEngine
            repo = KnowledgeGraphRepository(session)
            engine = KnowledgeGraphEngine(repo)
            context_text, subgraphs = await engine.get_graph_augmented_context(
                query=query, user_id=user_id, max_hops=max_hops
            )
            entities = await repo.list_entities(
                user_id=user_id, entity_type=entity_type, search=query, limit=10
            )
            return {
                "success": True,
                "query": query,
                "context": context_text,
                "entities_found": [e.to_dict() for e in entities],
                "subgraphs": subgraphs,
                "count": len(entities),
            }


class ExtractGraphTripletsTool(Tool):
    """Tool for extracting and storing entity-relation triplets into the Knowledge Graph."""

    schema = ToolSchema(
        name="extract_graph_triplets",
        description="Extract entities and relationship triplets from text and persist them into the knowledge graph.",
        parameters=[
            ToolParameter(
                name="text",
                type="string",
                description="Text, paragraph, or synthesis finding to extract triplets from.",
                required=True,
            ),
        ],
    )

    def __init__(
        self,
        repo: Optional[KnowledgeGraphRepository] = None,
        graph_engine: Optional[Any] = None,
    ) -> None:
        self._repo = repo
        self._engine = graph_engine

    async def execute(self, text: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute extraction and persistence of triplets."""
        user_id = kwargs.get("user_id")
        job_id = kwargs.get("job_id")

        if self._engine:
            res = await self._engine.extract_triplets_from_text(text, user_id=user_id, job_id=job_id)
            data = res.model_dump() if hasattr(res, "model_dump") else res
            return {"success": True, "data": data}

        if self._repo:
            from research.graph.engine import KnowledgeGraphEngine
            engine = KnowledgeGraphEngine(self._repo)
            res = await engine.extract_triplets_from_text(text, user_id=user_id, job_id=job_id)
            return {"success": True, "data": res.model_dump()}

        async with get_session() as session:
            from research.graph.engine import KnowledgeGraphEngine
            repo = KnowledgeGraphRepository(session)
            engine = KnowledgeGraphEngine(repo)
            res = await engine.extract_triplets_from_text(text, user_id=user_id, job_id=job_id)
            return {"success": True, "data": res.model_dump()}


class FindRelationPathTool(Tool):
    """Tool for finding multi-hop paths between two knowledge entities."""

    schema = ToolSchema(
        name="find_relation_path",
        description="Find multi-hop connections, chains, or relational paths connecting two entities in the knowledge graph.",
        parameters=[
            ToolParameter(
                name="source_entity",
                type="string",
                description="Starting entity name.",
                required=True,
            ),
            ToolParameter(
                name="target_entity",
                type="string",
                description="Target entity name.",
                required=True,
            ),
            ToolParameter(
                name="max_depth",
                type="integer",
                description="Maximum hop distance to search (default 4).",
                required=False,
                default=4,
            ),
        ],
    )

    def __init__(
        self,
        repo: Optional[KnowledgeGraphRepository] = None,
        graph_engine: Optional[Any] = None,
    ) -> None:
        self._repo = repo
        self._engine = graph_engine

    async def execute(
        self,
        source_entity: str,
        target_entity: str,
        max_depth: int = 4,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute path finding between entities."""
        user_id = kwargs.get("user_id")

        if self._engine:
            res = await self._engine.find_path_between_entities(
                source_name=source_entity,
                target_name=target_entity,
                user_id=user_id,
                max_depth=max_depth,
            )
            data = res.model_dump() if hasattr(res, "model_dump") else res
            return {"success": True, "data": data}

        if self._repo:
            from research.graph.engine import KnowledgeGraphEngine
            engine = KnowledgeGraphEngine(self._repo)
            res = await engine.find_path_between_entities(
                source_name=source_entity,
                target_name=target_entity,
                user_id=user_id,
                max_depth=max_depth,
            )
            return {"success": True, "data": res.model_dump()}

        async with get_session() as session:
            from research.graph.engine import KnowledgeGraphEngine
            repo = KnowledgeGraphRepository(session)
            engine = KnowledgeGraphEngine(repo)
            res = await engine.find_path_between_entities(
                source_name=source_entity,
                target_name=target_entity,
                user_id=user_id,
                max_depth=max_depth,
            )
            return {"success": True, "data": res.model_dump()}
