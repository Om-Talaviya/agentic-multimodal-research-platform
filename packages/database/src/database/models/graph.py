"""SQLAlchemy database models for Knowledge Graph entities and relations."""

from datetime import datetime, timezone
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID, JSONType


class DBKnowledgeEntity(Base):
    """Represents a canonical knowledge entity / node in the research knowledge graph."""

    __tablename__ = "knowledge_entities"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    project_id = Column(GUID, nullable=True, index=True)

    # Core identification
    name = Column(String(255), nullable=False, index=True)
    canonical_name = Column(String(255), nullable=False, index=True)  # lowercased / normalized
    entity_type = Column(
        String(50),
        nullable=False,
        default="CONCEPT",
        index=True,
    )  # CONCEPT, TECHNOLOGY, MATERIAL, PERSON, ORGANIZATION, METRIC, DATASET, PAPER, LOCATION

    description = Column(Text, nullable=True)
    aliases = Column(JSONType, nullable=False, default=list)  # List of alternate names / acronyms
    properties_json = Column(JSONType, nullable=False, default=dict)  # Metadata attributes
    confidence = Column(Float, nullable=False, default=1.0)  # 0.0 - 1.0

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    outgoing_relations = relationship(
        "DBKnowledgeRelation",
        foreign_keys="DBKnowledgeRelation.source_id",
        back_populates="source_entity",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    incoming_relations = relationship(
        "DBKnowledgeRelation",
        foreign_keys="DBKnowledgeRelation.target_id",
        back_populates="target_entity",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_knowledge_entities_user_canonical", "user_id", "canonical_name"),
        Index("ix_knowledge_entities_type_canonical", "entity_type", "canonical_name"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity model to dictionary representation."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "project_id": str(self.project_id) if self.project_id else None,
            "name": self.name,
            "canonical_name": self.canonical_name,
            "entity_type": self.entity_type,
            "description": self.description,
            "aliases": self.aliases or [],
            "properties": self.properties_json or {},
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DBKnowledgeRelation(Base):
    """Represents a directed relationship / edge between two knowledge entities."""

    __tablename__ = "knowledge_relations"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    project_id = Column(GUID, nullable=True, index=True)
    job_id = Column(GUID, ForeignKey("research_jobs.id", ondelete="SET NULL"), nullable=True, index=True)

    # Directed edge
    source_id = Column(
        GUID,
        ForeignKey("knowledge_entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_id = Column(
        GUID,
        ForeignKey("knowledge_entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    relation_type = Column(
        String(100),
        nullable=False,
        default="RELATES_TO",
        index=True,
    )  # AUTHORED_BY, USES_MATERIAL, CONTRADICTS, EVALUATED_ON, DEVELOPED_BY, CORRELATES_WITH, DERIVED_FROM, APPLIES_METHODOLOGY

    description = Column(Text, nullable=True)  # Human-readable claim / statement
    weight = Column(Float, nullable=False, default=1.0)  # Relationship weight / strength
    confidence = Column(Float, nullable=False, default=1.0)  # Extraction confidence
    evidence_id = Column(GUID, ForeignKey("evidence.id", ondelete="SET NULL"), nullable=True)

    properties_json = Column(JSONType, nullable=False, default=dict)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    source_entity = relationship(
        "DBKnowledgeEntity",
        foreign_keys=[source_id],
        back_populates="outgoing_relations",
        lazy="joined",
    )
    target_entity = relationship(
        "DBKnowledgeEntity",
        foreign_keys=[target_id],
        back_populates="incoming_relations",
        lazy="joined",
    )

    __table_args__ = (
        Index("ix_knowledge_relations_source_target", "source_id", "target_id"),
        Index("ix_knowledge_relations_type", "relation_type"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert relation model to dictionary representation."""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "project_id": str(self.project_id) if self.project_id else None,
            "job_id": str(self.job_id) if self.job_id else None,
            "source_id": str(self.source_id),
            "target_id": str(self.target_id),
            "source_name": self.source_entity.name if self.source_entity else None,
            "target_name": self.target_entity.name if self.target_entity else None,
            "relation_type": self.relation_type,
            "description": self.description,
            "weight": self.weight,
            "confidence": self.confidence,
            "evidence_id": str(self.evidence_id) if self.evidence_id else None,
            "properties": self.properties_json or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
