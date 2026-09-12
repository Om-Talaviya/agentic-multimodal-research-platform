"""Domain models for Knowledge Graph entities, relations, and GraphRAG context."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import uuid


class EntityType(str, Enum):
    """Standard categorized entity types."""
    CONCEPT = "CONCEPT"
    TECHNOLOGY = "TECHNOLOGY"
    MATERIAL = "MATERIAL"
    PERSON = "PERSON"
    ORGANIZATION = "ORGANIZATION"
    METRIC = "METRIC"
    DATASET = "DATASET"
    PAPER = "PAPER"
    LOCATION = "LOCATION"
    OTHER = "OTHER"


class RelationType(str, Enum):
    """Standard relation types / predicates in research graphs."""
    AUTHORED_BY = "AUTHORED_BY"
    USES_MATERIAL = "USES_MATERIAL"
    CONTRADICTS = "CONTRADICTS"
    EVALUATED_ON = "EVALUATED_ON"
    DEVELOPED_BY = "DEVELOPED_BY"
    CORRELATES_WITH = "CORRELATES_WITH"
    DERIVED_FROM = "DERIVED_FROM"
    APPLIES_METHODOLOGY = "APPLIES_METHODOLOGY"
    EXPOSED_TO = "EXPOSED_TO"
    HOSTS = "HOSTS"
    SECRETES = "SECRETES"
    ENHANCES = "ENHANCES"
    SYNTHESIZED_VIA = "SYNTHESIZED_VIA"
    RELATES_TO = "RELATES_TO"


class EntityNode(BaseModel):
    """Lightweight representation of an entity node."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    canonical_name: Optional[str] = None
    entity_type: EntityType = EntityType.CONCEPT
    description: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 1.0


class RelationEdge(BaseModel):
    """Lightweight representation of a directed relation edge."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    target_id: str
    source_name: Optional[str] = None
    target_name: Optional[str] = None
    relation_type: str = "RELATES_TO"
    description: Optional[str] = None
    weight: float = 1.0
    confidence: float = 1.0
    evidence_id: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphData(BaseModel):
    """Network subgraph containing nodes and edges."""
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    edges: List[Dict[str, Any]] = Field(default_factory=list)


class GraphTriplet(BaseModel):
    """Input triplet extracted from research evidence or text."""
    source: str
    source_type: str = "CONCEPT"
    relation: str = "RELATES_TO"
    target: str
    target_type: str = "CONCEPT"
    description: Optional[str] = None
    confidence: float = 1.0
    weight: float = 1.0


class GraphExtractionResult(BaseModel):
    """Result of automated entity and relation extraction."""
    entities_count: int
    relations_count: int
    triplets: List[GraphTriplet] = Field(default_factory=list)
    extracted_entities: List[str] = Field(default_factory=list)


class GraphPathStep(BaseModel):
    """Single step in a multi-hop graph path."""
    from_id: str
    to_id: str
    relation_id: str
    relation_type: str
    description: Optional[str] = None
    direction: str = "OUTGOING"


class GraphPathResult(BaseModel):
    """Result of path finding query between two entity nodes."""
    source_entity: str
    target_entity: str
    path_found: bool
    hop_count: int = 0
    steps: List[GraphPathStep] = Field(default_factory=list)
    summary: Optional[str] = None
