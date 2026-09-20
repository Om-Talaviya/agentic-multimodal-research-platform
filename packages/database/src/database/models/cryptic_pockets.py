"""
SQLAlchemy database models for Phase 107: Allosteric Pocket Discovery & Cryptic Binding Site Mapping.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID

class DBCrypticPocketAnalysis(Base):
    __tablename__ = "cryptic_pocket_analyses"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=True, index=True)
    target_protein = Column(String(255), nullable=False, index=True)
    pdb_id = Column(String(20), nullable=True, index=True)
    trajectory_frames_sampled = Column(Integer, default=100)
    detected_cryptic_pockets = Column(Integer, default=0)
    max_druggability_score = Column(Float, default=0.0)
    allosteric_coupling_score = Column(Float, default=0.0)
    metadata_json = Column(JSON, nullable=True)
    status = Column(String(50), default="COMPLETED")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    pockets = relationship("DBAllostericPocketProfile", back_populates="analysis", cascade="all, delete-orphan")
    coupled_networks = relationship("DBCoupledResidueNetwork", back_populates="analysis", cascade="all, delete-orphan")

class DBAllostericPocketProfile(Base):
    __tablename__ = "allosteric_pocket_profiles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(GUID(), ForeignKey("cryptic_pocket_analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    pocket_name = Column(String(100), nullable=False, index=True)
    center_x = Column(Float, default=0.0)
    center_y = Column(Float, default=0.0)
    center_z = Column(Float, default=0.0)
    apo_volume_a3 = Column(Float, default=0.0)
    holo_volume_a3 = Column(Float, default=0.0)
    volume_expansion_ratio = Column(Float, default=1.0)
    druggability_index = Column(Float, default=0.0)
    hydrophobicity_score = Column(Float, default=0.0)
    enclosing_residues = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("DBCrypticPocketAnalysis", back_populates="pockets")

class DBCoupledResidueNetwork(Base):
    __tablename__ = "coupled_residue_networks"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(GUID(), ForeignKey("cryptic_pocket_analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    source_residue = Column(String(50), nullable=False, index=True)
    target_residue = Column(String(50), nullable=False, index=True)
    allosteric_correlation = Column(Float, default=0.0)
    pathway_shortest_distance_a = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("DBCrypticPocketAnalysis", back_populates="coupled_networks")
