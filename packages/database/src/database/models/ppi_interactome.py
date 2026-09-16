"""
SQLAlchemy models for Protein-Protein Interaction (PPI) Complex Interactome (Phase 58).
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship

from database.connection import Base


class DBPPIInteractomeNetwork(Base):
    """Represents a biological PPI network graph."""
    __tablename__ = "ppi_networks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    network_name = Column(String(128), nullable=False)
    disease_context = Column(String(128), nullable=False)  # e.g., KRAS Oncogenic Signaling, Wnt/Beta-Catenin
    total_nodes = Column(Integer, default=0)
    total_edges = Column(Integer, default=0)
    status = Column(String(32), default="COMPLETED")
    metadata_info = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    nodes = relationship("DBProteinNode", back_populates="network", cascade="all, delete-orphan")
    edges = relationship("DBProteinInteractionEdge", back_populates="network", cascade="all, delete-orphan")


class DBProteinNode(Base):
    """Represents a protein node in the interactome."""
    __tablename__ = "ppi_protein_nodes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    network_id = Column(String(36), ForeignKey("ppi_networks.id", ondelete="CASCADE"), nullable=False)
    gene_symbol = Column(String(64), nullable=False)
    uniprot_id = Column(String(32), nullable=False)
    degree_centrality = Column(Float, default=0.0)
    betweenness_centrality = Column(Float, default=0.0)
    is_hub_target = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    network = relationship("DBPPIInteractomeNetwork", back_populates="nodes")


class DBProteinInteractionEdge(Base):
    """Represents a physical or regulatory PPI interaction edge."""
    __tablename__ = "ppi_interaction_edges"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    network_id = Column(String(36), ForeignKey("ppi_networks.id", ondelete="CASCADE"), nullable=False)
    source_protein = Column(String(64), nullable=False)
    target_protein = Column(String(64), nullable=False)
    interaction_type = Column(String(64), default="Physical Binding")  # Physical Binding, Phosphorylation, Ubiquitination
    binding_affinity_kd_nm = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)  # 0.0 - 1.0
    druggability_index = Column(Float, default=0.75)  # 0.0 - 1.0
    interface_surface_area_a2 = Column(Float, default=1450.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    network = relationship("DBPPIInteractomeNetwork", back_populates="edges")
