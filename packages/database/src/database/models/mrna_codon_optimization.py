"""Phase 153: Multi-Objective mRNA Codon Optimization Models."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBmRNACodonOptimizationCampaign(Base):
    """Multi-objective mRNA sequence codon optimization campaign."""

    __tablename__ = "mrna_codon_optimization_campaigns"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    target_protein_name = Column(String(255), nullable=False)
    expression_host = Column(String(120), default="Homo sapiens (Human)")
    original_cai = Column(Float, default=0.0)
    optimized_cai = Column(Float, default=0.0)
    gc_content_percent = Column(Float, default=0.0)
    mfe_secondary_struct_kcal_mol = Column(Float, default=0.0)
    uridine_depletion_percent = Column(Float, default=0.0)
    translation_efficiency_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    variants = relationship("DBOptimizedCodonVariant", back_populates="campaign", cascade="all, delete-orphan")
    cai_profiles = relationship("DBCAIProfilePoint", back_populates="campaign", cascade="all, delete-orphan")


class DBOptimizedCodonVariant(Base):
    """Optimized candidate mRNA transcript sequence."""

    __tablename__ = "optimized_codon_variants"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(GUID(), ForeignKey("mrna_codon_optimization_campaigns.id", ondelete="CASCADE"), nullable=False)
    variant_rank = Column(Integer, nullable=False)
    mrna_sequence = Column(Text, nullable=False)
    pareto_fitness_score = Column(Float, nullable=False)
    ribosome_dwell_time_ms = Column(Float, nullable=False)
    immunogenicity_risk_score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    campaign = relationship("DBmRNACodonOptimizationCampaign", back_populates="variants")


class DBCAIProfilePoint(Base):
    """Codon adaptation profile per window across transcript."""

    __tablename__ = "cai_profile_points"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(GUID(), ForeignKey("mrna_codon_optimization_campaigns.id", ondelete="CASCADE"), nullable=False)
    codon_position = Column(Integer, nullable=False)
    codon_triplet = Column(String(8), nullable=False)
    amino_acid = Column(String(8), nullable=False)
    relative_adaptiveness = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    campaign = relationship("DBmRNACodonOptimizationCampaign", back_populates="cai_profiles")
