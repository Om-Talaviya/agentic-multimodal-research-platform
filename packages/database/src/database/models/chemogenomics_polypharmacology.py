"""Chemogenomics Polypharmacology & Off-Target Interactome Models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base


class DBCompoundPolypharmacologyProfile(Base):
    """Compound multi-target binding screen and selectivity profile."""
    __tablename__ = "chemogenomics_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    compound_name = Column(String(128), nullable=False, index=True)
    smiles = Column(Text, nullable=False)
    primary_target = Column(String(128), nullable=False)
    gini_selectivity_index = Column(Float, nullable=False, default=0.5)  # 0.0 (promiscuous) - 1.0 (specific)
    selectivity_tier = Column(String(32), nullable=False, default="FAMILY_SELECTIVE")  # PAN_INHIBITOR, FAMILY_SELECTIVE, HIGHLY_SELECTIVE
    total_targets_screened = Column(Integer, nullable=False, default=50)
    off_target_liabilities_count = Column(Integer, nullable=False, default=0)
    profile_summary_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    affinities = relationship("DBTargetBindingAffinity", back_populates="profile", cascade="all, delete-orphan")
    alerts = relationship("DBOffTargetToxicityAlert", back_populates="profile", cascade="all, delete-orphan")


class DBTargetBindingAffinity(Base):
    """Binding affinity (IC50, Ki, Kd) against a single protein target."""
    __tablename__ = "target_binding_affinities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("chemogenomics_profiles.id", ondelete="CASCADE"), nullable=False)
    target_gene = Column(String(64), nullable=False, index=True)
    uniprot_id = Column(String(32), nullable=False)
    protein_family = Column(String(64), nullable=False, default="KINASE")  # KINASE, GPCR, ION_CHANNEL, NUCLEAR_RECEPTOR
    affinity_type = Column(String(16), nullable=False, default="IC50")  # IC50, KI, KD
    affinity_value_nm = Column(Float, nullable=False)  # in nanomolar (nM)
    is_primary_target = Column(Boolean, default=False)
    is_off_target_liability = Column(Boolean, default=False)

    profile = relationship("DBCompoundPolypharmacologyProfile", back_populates="affinities")


class DBOffTargetToxicityAlert(Base):
    """Antitarget safety alerts (hERG, 5-HT2B, BSEP, CYP3A4)."""
    __tablename__ = "off_target_toxicity_alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id = Column(String(36), ForeignKey("chemogenomics_profiles.id", ondelete="CASCADE"), nullable=False)
    target_gene = Column(String(64), nullable=False)
    risk_type = Column(String(64), nullable=False)  # CARDIOTOXICITY_HERG, VALVULOPATHY_5HT2B, HEPATOTOXICITY_BSEP, CYP_INHIBITION
    binding_potency_nm = Column(Float, nullable=False)
    severity = Column(String(16), nullable=False, default="HIGH")  # HIGH, MODERATE, LOW
    recommendation = Column(Text, nullable=False)

    profile = relationship("DBCompoundPolypharmacologyProfile", back_populates="alerts")
