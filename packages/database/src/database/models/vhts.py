"""
SQLAlchemy models for Autonomous Virtual High-Throughput Screening (vHTS) (Phase 54).
Implements ultra-large chemical library docking simulations, Vina energy scoring, and scaffold clustering.
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


class DBVirtualHTSScreen(Base):
    """Represents a virtual High-Throughput Screening (vHTS) campaign."""
    __tablename__ = "vhts_screens"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    target_protein_name = Column(String(255), nullable=False)
    pdb_id = Column(String(10), nullable=False)  # e.g., 7L11, 4ZAU
    binding_pocket_box = Column(JSON, nullable=False, default=dict)  # center {x,y,z}, size {x,y,z}
    library_source = Column(String(100), nullable=False, default="Enamine_REAL_10M")
    total_screened_compounds = Column(Integer, default=0)
    top_hits_count = Column(Integer, default=0)
    best_affinity_kcal_mol = Column(Float, default=0.0)
    status = Column(String(50), default="COMPLETED")  # RUNNING, COMPLETED, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    hits = relationship(
        "DBVirtualHTSHit",
        back_populates="screen",
        cascade="all, delete-orphan",
        order_by="DBVirtualHTSHit.docking_score_kcal_mol.asc()",
    )
    clusters = relationship(
        "DBHTSClusterGroup",
        back_populates="screen",
        cascade="all, delete-orphan",
        order_by="DBHTSClusterGroup.mean_affinity_kcal_mol.asc()",
    )


class DBVirtualHTSHit(Base):
    """Represents a top-ranked small molecule hit from a vHTS docking run."""
    __tablename__ = "vhts_hits"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    screen_id = Column(String(36), ForeignKey("vhts_screens.id", ondelete="CASCADE"), nullable=False, index=True)
    compound_id = Column(String(100), nullable=False)
    smiles = Column(Text, nullable=False)
    docking_score_kcal_mol = Column(Float, nullable=False)  # negative score, e.g. -11.4 kcal/mol
    cwas_energy = Column(Float, default=0.0)
    pains_filter_passed = Column(Boolean, default=True)
    rmsd_to_reference = Column(Float, default=0.0)
    pose_coordinates_json = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    screen = relationship("DBVirtualHTSScreen", back_populates="hits")


class DBHTSClusterGroup(Base):
    """Represents a Murcko scaffold structural cluster among top screening hits."""
    __tablename__ = "vhts_clusters"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    screen_id = Column(String(36), ForeignKey("vhts_screens.id", ondelete="CASCADE"), nullable=False, index=True)
    cluster_label = Column(String(100), nullable=False)
    scaffold_smiles = Column(Text, nullable=False)
    member_hits_count = Column(Integer, default=1)
    mean_affinity_kcal_mol = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    screen = relationship("DBVirtualHTSScreen", back_populates="clusters")
