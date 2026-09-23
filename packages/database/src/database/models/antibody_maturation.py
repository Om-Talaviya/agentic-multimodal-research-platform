"""
Phase 127: Autonomous In-Silico Antibody Affinity Maturation & Somatic Hypermutation Models.
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID, JSON


class DBAntibodyAffinityMaturation(Base):
    __tablename__ = "antibody_affinity_maturations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(String(100), nullable=True)
    candidate_name = Column(String(200), nullable=False)
    target_antigen = Column(String(200), nullable=False)
    parental_kd_nm = Column(Float, nullable=False, default=12.4)
    matured_kd_nm = Column(Float, nullable=False, default=0.18)
    affinity_fold_improvement = Column(Float, nullable=False, default=68.8)
    humanness_score_oasis = Column(Float, nullable=False, default=0.89)
    thermostability_tm_celsius = Column(Float, nullable=False, default=74.5)
    evolution_rounds = Column(Integer, nullable=False, default=4)
    metadata_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    variants = relationship("DBDirectedEvolutionVariant", back_populates="campaign", cascade="all, delete-orphan")
    contacts = relationship("DBParatopeEpitopeContact", back_populates="campaign", cascade="all, delete-orphan")


class DBDirectedEvolutionVariant(Base):
    __tablename__ = "antibody_evolution_variants"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(GUID(), ForeignKey("antibody_affinity_maturations.id", ondelete="CASCADE"), nullable=False)
    variant_id = Column(String(100), nullable=False)
    cdr_region = Column(String(50), nullable=False)  # CDR-H3, CDR-H2, CDR-L3, etc.
    mutations_summary = Column(String(255), nullable=False)  # e.g., "Y102W, G104R"
    predicted_binding_energy_ddg = Column(Float, nullable=False, default=-2.45)
    dissociation_constant_kd_nm = Column(Float, nullable=False, default=0.22)
    developability_flag = Column(Boolean, nullable=False, default=True)
    polyreactivity_risk = Column(Float, nullable=False, default=0.04)
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("DBAntibodyAffinityMaturation", back_populates="variants")


class DBParatopeEpitopeContact(Base):
    __tablename__ = "antibody_paratope_contacts"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(GUID(), ForeignKey("antibody_affinity_maturations.id", ondelete="CASCADE"), nullable=False)
    antibody_residue = Column(String(50), nullable=False)  # e.g., "Trp102H"
    antigen_residue = Column(String(50), nullable=False)   # e.g., "Lys417Antigen"
    interaction_type = Column(String(50), nullable=False)  # HydrogenBond, SaltBridge, PiStacking, Hydrophobic
    interaction_distance_angstrom = Column(Float, nullable=False, default=2.85)
    binding_energy_contribution_kcal = Column(Float, nullable=False, default=-1.65)
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("DBAntibodyAffinityMaturation", back_populates="contacts")
