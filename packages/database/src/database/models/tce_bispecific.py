"""TCE Models (Phase 113)."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID

class DBTCEConstructDesign(Base):
    __tablename__ = "tce_construct_designs"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    construct_name = Column(String(100), nullable=False)
    tumor_target_antigen = Column(String(100), nullable=False)
    tcell_effector_arm = Column(String(100), default="Anti-CD3e UCHT1", nullable=False)
    format_geometry = Column(String(100), default="BiTE (scFv-scFv)", nullable=False)
    linker_length_amino_acids = Column(Integer, default=15, nullable=False)
    synapse_distance_angstroms = Column(Float, default=42.5, nullable=False)
    cytotoxicity_ec50_pm = Column(Float, default=12.4, nullable=False)
    crs_safety_index = Column(Float, default=85.2, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    synapse_metrics = relationship("DBSynapseGeometryMetric", back_populates="construct", cascade="all, delete-orphan")

class DBSynapseGeometryMetric(Base):
    __tablename__ = "tce_synapse_metrics"
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    construct_id = Column(GUID(), ForeignKey("tce_construct_designs.id", ondelete="CASCADE"), nullable=False, index=True)
    intermembrane_distance_nm = Column(Float, nullable=False)
    cd45_exclusion_efficiency = Column(Float, default=94.5, nullable=False)
    perforin_granzyme_flux_score = Column(Float, default=88.2, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    construct = relationship("DBTCEConstructDesign", back_populates="synapse_metrics")
