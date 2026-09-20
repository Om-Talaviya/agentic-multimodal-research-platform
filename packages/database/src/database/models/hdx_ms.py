"""
SQLAlchemy database models for Phase 105: Hydrogen-Deuterium Exchange Mass Spectrometry (HDX-MS).
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID

class DBHDXExperiment(Base):
    __tablename__ = "hdx_experiments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), nullable=True, index=True)
    protein_name = Column(String(255), nullable=False, index=True)
    uniprot_id = Column(String(50), nullable=True, index=True)
    state_condition = Column(String(100), default="APO", index=True)
    total_peptides = Column(Integer, default=0)
    sequence_coverage_pct = Column(Float, default=0.0)
    redundancy_score = Column(Float, default=0.0)
    deuteration_buffer_ph = Column(Float, default=7.4)
    temperature_celsius = Column(Float, default=20.0)
    metadata_json = Column(JSON, nullable=True)
    status = Column(String(50), default="COMPLETED")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    uptake_curves = relationship("DBDeuteriumUptakeCurve", back_populates="experiment", cascade="all, delete-orphan")
    protection_maps = relationship("DBProtectionFactorMap", back_populates="experiment", cascade="all, delete-orphan")

class DBDeuteriumUptakeCurve(Base):
    __tablename__ = "hdx_deuterium_uptake_curves"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(GUID(), ForeignKey("hdx_experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    peptide_sequence = Column(String(100), nullable=False, index=True)
    start_res = Column(Integer, nullable=False)
    end_res = Column(Integer, nullable=False)
    timepoint_seconds = Column(Float, nullable=False)
    deuterium_uptake_da = Column(Float, default=0.0)
    fractional_uptake_pct = Column(Float, default=0.0)
    protection_factor_ln_p = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    experiment = relationship("DBHDXExperiment", back_populates="uptake_curves")

class DBProtectionFactorMap(Base):
    __tablename__ = "hdx_protection_factor_maps"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(GUID(), ForeignKey("hdx_experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    residue_number = Column(Integer, nullable=False)
    amino_acid = Column(String(5), nullable=False)
    protection_factor = Column(Float, default=1.0)
    solvent_accessibility_level = Column(String(50), default="EXPOSED")
    delta_uptake_apo_vs_bound = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    experiment = relationship("DBHDXExperiment", back_populates="protection_maps")
