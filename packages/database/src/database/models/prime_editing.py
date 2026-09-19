"""CRISPR Prime & Base Editing Database Models (Phase 101)."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID


class DBPrimeEditingDesign(Base):
    __tablename__ = "prime_editing_designs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    target_gene = Column(String(100), nullable=False)  # e.g., HBB (Sickle Cell E6V), CFTR (F508del), HEXA
    genomic_locus = Column(String(100), nullable=False)
    intended_edit_type = Column(String(50), nullable=False)  # POINT_MUTATION, INSERTION, DELETION, BASE_CONVERSION
    editor_architecture = Column(String(100), default="PEmax_PE3", nullable=False)  # PE2, PE3, PE3b, PEmax, ABE8e, CBE4max
    predicted_editing_efficiency_pct = Column(Float, default=64.8, nullable=False)
    purity_score_pct = Column(Float, default=92.5, nullable=False)
    indel_frequency_pct = Column(Float, default=1.8, nullable=False)
    design_metadata = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    pegrna_candidates = relationship("DBPegRnaCandidate", back_populates="design", cascade="all, delete-orphan")
    bystander_alerts = relationship("DBBystanderEditingAlert", back_populates="design", cascade="all, delete-orphan")


class DBPegRnaCandidate(Base):
    __tablename__ = "pegrna_candidates"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    design_id = Column(GUID(), ForeignKey("prime_editing_designs.id", ondelete="CASCADE"), nullable=False, index=True)
    spacer_sequence = Column(String(50), nullable=False)
    pbs_sequence = Column(String(50), nullable=False)
    pbs_length_nt = Column(Integer, default=13, nullable=False)
    pbs_tm_celsius = Column(Float, default=37.5, nullable=False)
    rtt_sequence = Column(String(100), nullable=False)
    rtt_length_nt = Column(Integer, default=16, nullable=False)
    nicking_guide_spacer = Column(String(50), nullable=True)
    candidate_rank = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    design = relationship("DBPrimeEditingDesign", back_populates="pegrna_candidates")


class DBBystanderEditingAlert(Base):
    __tablename__ = "bystander_editing_alerts"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    design_id = Column(GUID(), ForeignKey("prime_editing_designs.id", ondelete="CASCADE"), nullable=False, index=True)
    position_in_window = Column(Integer, nullable=False)
    bystander_base = Column(String(10), nullable=False)  # C, A
    deamination_risk_score = Column(Float, nullable=False)  # 0.0 to 1.0
    synonymous_flag = Column(String(50), default="MISSENSE_MUTATION", nullable=False)  # SYNONYMOUS, MISSENSE_MUTATION, INTRONIC
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    design = relationship("DBPrimeEditingDesign", back_populates="bystander_alerts")
