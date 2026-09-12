"""API endpoints for Knowledge Graph (Generation 3: Autonomous Research)."""

from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from api.dependencies import (
    get_current_user,
    get_graph_engine,
    get_graph_repository,
    get_optional_current_user,
)
from database.models.graph import DBKnowledgeEntity, DBKnowledgeRelation
from database.repositories.graph_repo import KnowledgeGraphRepository
from research.graph.engine import KnowledgeGraphEngine
from research.graph.models import (
    EntityType,
    GraphExtractionResult,
    GraphPathResult,
    RelationType,
)
from shared.auth import User
from shared.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/graph", tags=["graph"])


# --- Pydantic Request/Response Models ---

class CreateEntityRequest(BaseModel):
    name: str = Field(..., min_length=1, description="Entity or concept name")
    canonical_name: Optional[str] = Field(default=None, description="Resolved canonical name")
    entity_type: str = Field(default="CONCEPT", description="Entity category")
    description: Optional[str] = Field(default=None, description="Detailed description")
    aliases: List[str] = Field(default_factory=list, description="Synonyms or alias names")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Metadata key-values")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")


class CreateRelationRequest(BaseModel):
    source_id: str = Field(..., description="Source entity UUID")
    target_id: str = Field(..., description="Target entity UUID")
    relation_type: str = Field(default="RELATES_TO", description="Relationship predicate")
    description: Optional[str] = Field(default=None, description="Relationship context")
    weight: float = Field(default=1.0, description="Connection strength")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")
    evidence_id: Optional[str] = Field(default=None, description="Optional evidence UUID")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Edge properties")


class ExtractTripletsRequest(BaseModel):
    text: str = Field(..., min_length=5, description="Text snippet to extract entities and relations from")
    job_id: Optional[str] = Field(default=None, description="Optional associated research job ID")
    persist: bool = Field(default=True, description="Whether to persist extracted triplets to the database")


class EntityResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    name: str
    canonical_name: str
    entity_type: str
    description: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class RelationResponse(BaseModel):
    id: str
    source_id: str
    target_id: str
    source_name: Optional[str] = None
    target_name: Optional[str] = None
    relation_type: str
    description: Optional[str] = None
    weight: float = 1.0
    confidence: float = 1.0
    evidence_id: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None


class GraphStatsResponse(BaseModel):
    total_entities: int
    total_relations: int
    entity_type_counts: Dict[str, int] = Field(default_factory=dict)


# --- Endpoints ---

@router.get("/nodes", response_model=List[Dict[str, Any]])
async def list_entities(
    entity_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: Optional[User] = Depends(get_optional_current_user),
    repo: KnowledgeGraphRepository = Depends(get_graph_repository),
) -> List[Dict[str, Any]]:
    """List knowledge entities with optional filtering."""
    user_uuid = UUID(str(current_user.id)) if current_user else None
    entities = await repo.list_entities(
        user_id=user_uuid,
        entity_type=entity_type,
        search=search,
        limit=limit,
        offset=offset,
    )
    return [e.to_dict() for e in entities]


@router.post("/nodes", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_entity(
    req: CreateEntityRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    repo: KnowledgeGraphRepository = Depends(get_graph_repository),
) -> Dict[str, Any]:
    """Create a new entity in the knowledge graph."""
    user_uuid = UUID(str(current_user.id)) if current_user else None
    entity = await repo.create_entity(
        name=req.name,
        canonical_name=req.canonical_name,
        entity_type=req.entity_type,
        user_id=user_uuid,
        description=req.description,
        aliases=req.aliases,
        properties=req.properties,
        confidence=req.confidence,
    )
    return entity.to_dict()


@router.get("/nodes/{node_id}", response_model=Dict[str, Any])
async def get_entity(
    node_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    repo: KnowledgeGraphRepository = Depends(get_graph_repository),
) -> Dict[str, Any]:
    """Get entity details by UUID."""
    try:
        uuid_val = UUID(node_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid node UUID")

    entity = await repo.get_entity_by_id(uuid_val)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    return entity.to_dict()


@router.delete("/nodes/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entity(
    node_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    repo: KnowledgeGraphRepository = Depends(get_graph_repository),
) -> None:
    """Delete an entity and its connected relations."""
    try:
        uuid_val = UUID(node_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid node UUID")

    success = await repo.delete_entity(uuid_val)
    if not success:
        raise HTTPException(status_code=404, detail="Entity not found")


@router.get("/edges", response_model=List[Dict[str, Any]])
async def list_relations(
    source_id: Optional[str] = None,
    target_id: Optional[str] = None,
    relation_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: Optional[User] = Depends(get_optional_current_user),
    repo: KnowledgeGraphRepository = Depends(get_graph_repository),
) -> List[Dict[str, Any]]:
    """List relational edges between entities."""
    s_uuid = UUID(source_id) if source_id else None
    t_uuid = UUID(target_id) if target_id else None

    relations = await repo.list_relations(
        source_id=s_uuid,
        target_id=t_uuid,
        relation_type=relation_type,
        limit=limit,
        offset=offset,
    )
    return [r.to_dict() for r in relations]


@router.post("/edges", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_relation(
    req: CreateRelationRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    repo: KnowledgeGraphRepository = Depends(get_graph_repository),
) -> Dict[str, Any]:
    """Create a directed relation between two entities."""
    try:
        s_uuid = UUID(req.source_id)
        t_uuid = UUID(req.target_id)
        ev_uuid = UUID(req.evidence_id) if req.evidence_id else None
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID for source, target, or evidence")

    relation = await repo.create_relation(
        source_id=s_uuid,
        target_id=t_uuid,
        relation_type=req.relation_type,
        description=req.description,
        weight=req.weight,
        confidence=req.confidence,
        evidence_id=ev_uuid,
        properties=req.properties,
    )
    return relation.to_dict()


@router.delete("/edges/{edge_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_relation(
    edge_id: str,
    current_user: Optional[User] = Depends(get_optional_current_user),
    repo: KnowledgeGraphRepository = Depends(get_graph_repository),
) -> None:
    """Delete a relation edge."""
    try:
        uuid_val = UUID(edge_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid edge UUID")

    success = await repo.delete_relation(uuid_val)
    if not success:
        raise HTTPException(status_code=404, detail="Relation not found")


@router.get("/subgraph", response_model=Dict[str, Any])
async def get_subgraph(
    center_entity_id: Optional[str] = None,
    query: Optional[str] = None,
    k_hops: int = Query(1, ge=1, le=3),
    current_user: Optional[User] = Depends(get_optional_current_user),
    repo: KnowledgeGraphRepository = Depends(get_graph_repository),
) -> Dict[str, Any]:
    """Retrieve an interactive k-hop neighborhood graph centered around an entity or keyword."""
    center_uuid = None
    if center_entity_id:
        try:
            center_uuid = UUID(center_entity_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid center_entity_id UUID")
    elif query:
        entity = await repo.find_entity_by_name(query)
        if entity:
            center_uuid = entity.id

    if not center_uuid:
        # If no center specified, return top entities and relations
        entities = await repo.list_entities(limit=100)
        relations = await repo.list_relations(limit=200)
        return {
            "nodes": [e.to_dict() for e in entities],
            "edges": [r.to_dict() for r in relations],
            "center_id": None,
            "k_hops": k_hops,
        }

    return await repo.get_k_hop_subgraph(center_uuid, max_hops=k_hops)


@router.get("/paths", response_model=Dict[str, Any])
async def find_paths(
    source: str = Query(..., min_length=1, description="Source entity name or UUID"),
    target: str = Query(..., min_length=1, description="Target entity name or UUID"),
    max_depth: int = Query(4, ge=1, le=6),
    current_user: Optional[User] = Depends(get_optional_current_user),
    engine: KnowledgeGraphEngine = Depends(get_graph_engine),
) -> Dict[str, Any]:
    """Find multi-hop relational path connecting two entities."""
    user_id_str = str(current_user.id) if current_user else None
    res = await engine.find_path_between_entities(
        source_name=source,
        target_name=target,
        user_id=user_id_str,
        max_depth=max_depth,
    )
    return res.model_dump()


@router.post("/extract", response_model=Dict[str, Any])
async def extract_triplets(
    req: ExtractTripletsRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    engine: KnowledgeGraphEngine = Depends(get_graph_engine),
) -> Dict[str, Any]:
    """Extract entities and relationship triplets from text and persist to graph."""
    user_id_str = str(current_user.id) if current_user else None
    res = await engine.extract_triplets_from_text(
        text=req.text,
        user_id=user_id_str,
        job_id=req.job_id,
    )
    return res.model_dump()


@router.get("/stats", response_model=GraphStatsResponse)
async def get_graph_stats(
    current_user: Optional[User] = Depends(get_optional_current_user),
    repo: KnowledgeGraphRepository = Depends(get_graph_repository),
) -> GraphStatsResponse:
    """Get global counts and metrics for the Knowledge Graph."""
    user_uuid = UUID(str(current_user.id)) if current_user else None
    total_entities = await repo.count_entities(user_id=user_uuid)
    relations = await repo.list_relations(limit=1000)
    entities = await repo.list_entities(user_id=user_uuid, limit=1000)
    
    type_counts: Dict[str, int] = {}
    for e in entities:
        t = e.entity_type or "CONCEPT"
        type_counts[t] = type_counts.get(t, 0) + 1

    return GraphStatsResponse(
        total_entities=total_entities,
        total_relations=len(relations),
        entity_type_counts=type_counts,
    )
