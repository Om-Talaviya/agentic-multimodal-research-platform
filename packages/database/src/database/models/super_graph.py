"""Database models for Multi-Modal Scientific Knowledge Super-Graph & Hypothesis Discovery (Phase 44)."""
from datetime import datetime, timezone
import uuid
from typing import List, Optional, Dict, Any

from sqlalchemy import String, Float, Integer, ForeignKey, Text, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from database.models.memory import GUID, JSONType

class DBSuperGraphNode(Base):
    __tablename__ = "supergraph_nodes"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True)
    project_id: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    
    canonical_id: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., HGNC:PCSK9, CHEBI:1234, MESH:D005909
    label: Mapped[str] = mapped_column(String(255), nullable=False)  # e.g., PCSK9, Glioblastoma, Evolocumab
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)  # Gene, Protein, Disease, Chemical, Pathway, CellType
    
    degree_centrality: Mapped[float] = mapped_column(Float, default=0.0)
    pagerank_score: Mapped[float] = mapped_column(Float, default=0.0)
    embedding_vector: Mapped[Optional[List[float]]] = mapped_column(JSONType, nullable=True)
    properties: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_sg_node_canonical", "canonical_id"),
        Index("ix_sg_node_type", "entity_type"),
    )

class DBSuperGraphEdge(Base):
    __tablename__ = "supergraph_edges"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_node_id: Mapped[str] = mapped_column(GUID(), ForeignKey("supergraph_nodes.id", ondelete="CASCADE"), nullable=False)
    target_node_id: Mapped[str] = mapped_column(GUID(), ForeignKey("supergraph_nodes.id", ondelete="CASCADE"), nullable=False)
    
    relation_type: Mapped[str] = mapped_column(String(100), nullable=False)  # INHIBITS, TARGETS, ASSOCIATED_WITH, BIOMARKER_OF
    confidence_score: Mapped[float] = mapped_column(Float, default=0.85)  # 0.0 to 1.0
    evidence_count: Mapped[int] = mapped_column(Integer, default=1)
    is_predicted: Mapped[bool] = mapped_column(Boolean, default=False)  # True if inferred via GNN Link Prediction
    
    meta_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_sg_edge_source", "source_node_id"),
        Index("ix_sg_edge_target", "target_node_id"),
        Index("ix_sg_edge_relation", "relation_type"),
    )

class DBCausalHypothesis(Base):
    __tablename__ = "causal_hypotheses"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True)
    project_id: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    premise_statement: Mapped[Text] = mapped_column(Text, nullable=False)
    mechanistic_chain: Mapped[Optional[List[str]]] = mapped_column(JSONType, nullable=True)  # [A -> B -> C]
    
    novelty_score: Mapped[float] = mapped_column(Float, default=0.88)  # 0.0 to 1.0
    biological_plausibility: Mapped[float] = mapped_column(Float, default=0.92)  # GNN consensus score
    falsifiability_index: Mapped[float] = mapped_column(Float, default=0.85)
    
    recommended_experiment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="proposed")  # proposed, validating, supported, refuted
    
    meta_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("ix_hypo_novelty", "novelty_score"),
        Index("ix_hypo_status", "status"),
    )
