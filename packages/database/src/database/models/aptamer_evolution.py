"""In-Silico SELEX Nucleic Acid Aptamer Evolution Models (Phase 143)."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import JSON, GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBAptamerEvolutionCampaign(Base):
    """Iterative in-silico SELEX selection campaign."""

    __tablename__ = "aptamer_evolution_campaigns"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    target_protein_name = Column(String(255), nullable=False)
    aptamer_type = Column(String(50), default="RNA")  # RNA or ssDNA
    initial_pool_size = Column(Integer, default=1000000)
    selection_rounds = Column(Integer, default=8)
    top_kd_nanomolar = Column(Float, default=0.0)
    consensus_motif = Column(String(255), default="")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    round_sequences = relationship("DBAptamerRoundSequence", back_populates="campaign", cascade="all, delete-orphan")
    binding_records = relationship("DBAptamerTargetBindingRecord", back_populates="campaign", cascade="all, delete-orphan")


class DBAptamerRoundSequence(Base):
    """Enriched sequence variant at a specific selection round."""

    __tablename__ = "aptamer_round_sequences"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(GUID(), ForeignKey("aptamer_evolution_campaigns.id", ondelete="CASCADE"), nullable=False)
    round_number = Column(Integer, nullable=False)
    sequence_string = Column(String(200), nullable=False)
    enrichment_fold = Column(Float, default=1.0)
    secondary_structure_dot_bracket = Column(String(200), default="")
    free_energy_kcal_mol = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    campaign = relationship("DBAptamerEvolutionCampaign", back_populates="round_sequences")


class DBAptamerTargetBindingRecord(Base):
    """Equilibrium dissociation constant Kd and binding specificity record."""

    __tablename__ = "aptamer_target_binding_records"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(GUID(), ForeignKey("aptamer_evolution_campaigns.id", ondelete="CASCADE"), nullable=False)
    aptamer_lead_id = Column(String(100), nullable=False)
    target_epitope_residues = Column(String(255), default="")
    kd_nanomolar = Column(Float, nullable=False)
    off_target_selectivity_ratio = Column(Float, default=1.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    campaign = relationship("DBAptamerEvolutionCampaign", back_populates="binding_records")
