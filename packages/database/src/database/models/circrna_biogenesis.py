"""SQLAlchemy models for Phase 179: Autonomous circRNA Back-Splicing Biogenesis & miRNA Sponge Matrix."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CircRNABiogenesisStudy(Base):
    """Study record for circular RNA back-splicing prediction and miRNA sponging capacity."""

    __tablename__ = "circrna_biogenesis_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    host_gene_symbol = Column(String(100), nullable=False)
    genomic_locus = Column(String(200), nullable=False)
    exon_count = Column(Integer, nullable=False, default=3)
    flanking_alu_elements_count = Column(Integer, nullable=False, default=2)
    backsplice_efficiency_score = Column(Float, nullable=False, default=0.88)
    circular_form_half_life_hours = Column(Float, nullable=False, default=48.5)
    total_mirna_sponge_binding_sites = Column(Integer, nullable=False, default=14)
    quaking_rbp_affinity_score = Column(Float, nullable=False, default=0.92)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    backsplice_junctions = relationship("CircRNABackspliceJunction", back_populates="study", cascade="all, delete-orphan")
    mirna_sponge_targets = relationship("CircRNAMiRNASpongeTarget", back_populates="study", cascade="all, delete-orphan")


class CircRNABackspliceJunction(Base):
    """Specific back-splice non-canonical exon junction coordinates."""

    __tablename__ = "circrna_backsplice_junctions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("circrna_biogenesis_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    junction_id = Column(String(100), nullable=False)
    donor_exon = Column(Integer, nullable=False)
    acceptor_exon = Column(Integer, nullable=False)
    junction_sequence = Column(String(200), nullable=False)
    junction_reads_ratio = Column(Float, nullable=False, default=0.34)
    flanking_repeat_match_score = Column(Float, nullable=False, default=0.91)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CircRNABiogenesisStudy", back_populates="backsplice_junctions")


class CircRNAMiRNASpongeTarget(Base):
    """miRNA sponge binding sites on the circular transcript."""

    __tablename__ = "circrna_mirna_sponge_targets"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("circrna_biogenesis_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    mirna_family = Column(String(100), nullable=False)  # e.g., miR-7-5p
    binding_site_start = Column(Integer, nullable=False)
    binding_site_end = Column(Integer, nullable=False)
    seed_match_type = Column(String(50), nullable=False, default="8mer")
    binding_free_energy_kcal_mol = Column(Float, nullable=False, default=-24.5)
    inhibition_potency_score = Column(Float, nullable=False, default=0.94)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CircRNABiogenesisStudy", back_populates="mirna_sponge_targets")
