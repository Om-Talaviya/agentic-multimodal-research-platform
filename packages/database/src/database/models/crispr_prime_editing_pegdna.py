"""SQLAlchemy models for Phase 180: Autonomous Prime Editing pegRNA Design & Flap Kinetics Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class PrimeEditingPegDNAStudy(Base):
    """Study record for CRISPR prime editing guide RNA (pegRNA) synthesis and flap kinetics."""

    __tablename__ = "prime_editing_pegdna_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_gene = Column(String(100), nullable=False)
    intended_mutation_type = Column(String(100), nullable=False, default="point_substitution")
    pbs_length_nt = Column(Integer, nullable=False, default=13)
    rtt_length_nt = Column(Integer, nullable=False, default=15)
    nick_to_edit_distance_bp = Column(Integer, nullable=False, default=3)
    predicted_prime_editing_efficiency = Column(Float, nullable=False, default=0.68)
    indel_byproduct_frequency = Column(Float, nullable=False, default=0.035)
    flap_equilibrium_ratio = Column(Float, nullable=False, default=3.42)
    pe_system_version = Column(String(50), nullable=False, default="PEmax_epegRNA")
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    pegdna_designs = relationship("PegDNASpacerPBSRTTDesign", back_populates="study", cascade="all, delete-orphan")
    flap_metrics = relationship("PegDNAFlapEquilibriumMetric", back_populates="study", cascade="all, delete-orphan")


class PegDNASpacerPBSRTTDesign(Base):
    """Candidate pegRNA constructs with full sequence architecture."""

    __tablename__ = "pegdna_spacer_pbs_rtt_designs"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("prime_editing_pegdna_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    candidate_id = Column(String(100), nullable=False)
    spacer_sequence_20nt = Column(String(50), nullable=False)
    pbs_sequence = Column(String(50), nullable=False)
    rtt_sequence_with_edit = Column(String(100), nullable=False)
    tevpre_structural_motif = Column(String(100), nullable=False, default="tevpre_hairpin")
    deep_pe_score = Column(Float, nullable=False, default=0.84)
    melting_temp_pbs_celsius = Column(Float, nullable=False, default=38.5)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("PrimeEditingPegDNAStudy", back_populates="pegdna_designs")


class PegDNAFlapEquilibriumMetric(Base):
    """3' Flap vs 5' Flap hybridization thermodynamics and ligation preference."""

    __tablename__ = "pegdna_flap_equilibrium_metrics"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("prime_editing_pegdna_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    flap_position_nt = Column(Integer, nullable=False)
    gibbs_free_energy_edited_flap_kcal = Column(Float, nullable=False)
    gibbs_free_energy_unmodified_flap_kcal = Column(Float, nullable=False)
    fen1_endonuclease_cleavage_rate = Column(Float, nullable=False)
    incorporation_probability = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("PrimeEditingPegDNAStudy", back_populates="flap_metrics")
