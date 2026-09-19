"""Oligonucleotide & siRNA Therapeutic Off-Target Database Models (Phase 98)."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID


class DBSiRnaDesign(Base):
    __tablename__ = "sirna_designs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    target_gene = Column(String(100), nullable=False)  # e.g., TTR, PCSK9, HTT
    sense_sequence = Column(String(100), nullable=False)
    antisense_sequence = Column(String(100), nullable=False)
    knockdown_potency_score = Column(Float, default=93.4, nullable=False)  # 0 to 100
    on_target_efficiency_score = Column(Float, default=89.2, nullable=False)
    thermodynamic_end_asymmetry = Column(Float, default=-3.2, nullable=False)  # kcal/mol delta-delta-G
    tlr_immunogenicity_risk = Column(String(50), default="LOW", nullable=False)  # LOW, MODERATE, HIGH
    off_target_safety_score = Column(Float, default=95.8, nullable=False)
    design_metadata = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    off_target_hits = relationship("DBSiRnaOffTargetHit", back_populates="design", cascade="all, delete-orphan")
    modifications = relationship("DBChemicalModificationPattern", back_populates="design", cascade="all, delete-orphan")


class DBSiRnaOffTargetHit(Base):
    __tablename__ = "sirna_off_target_hits"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    design_id = Column(GUID(), ForeignKey("sirna_designs.id", ondelete="CASCADE"), nullable=False, index=True)
    off_target_gene = Column(String(100), nullable=False)
    transcript_id = Column(String(100), nullable=False)
    seed_region_mismatches = Column(Integer, default=1, nullable=False)
    total_mismatches = Column(Integer, default=3, nullable=False)
    predicted_repression_pct = Column(Float, default=4.2, nullable=False)
    risk_tier = Column(String(50), default="NEGLIGIBLE", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    design = relationship("DBSiRnaDesign", back_populates="off_target_hits")


class DBChemicalModificationPattern(Base):
    __tablename__ = "sirna_chemical_modifications"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    design_id = Column(GUID(), ForeignKey("sirna_designs.id", ondelete="CASCADE"), nullable=False, index=True)
    strand = Column(String(20), default="ANTISENSE", nullable=False)  # SENSE, ANTISENSE
    position = Column(Integer, nullable=False)
    modification_type = Column(String(50), default="2_O_METHYL", nullable=False)  # 2_O_METHYL, 2_FLUORO, PHOSPHOROTHIOATE
    nuclease_stability_factor = Column(Float, default=12.5, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    design = relationship("DBSiRnaDesign", back_populates="modifications")
