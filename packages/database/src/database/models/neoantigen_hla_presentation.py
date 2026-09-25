"""SQLAlchemy models for Phase 185: Tumor Neoantigen Proteasomal Cleavage & HLA Presentation."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class NeoantigenHLAStudy(Base):
    """Study record for tumor neoantigen somatic mutation processing, TAP transport, and HLA-I/II presentation."""

    __tablename__ = "neoantigen_hla_presentation_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    patient_tumor_id = Column(String(100), nullable=False)
    patient_hla_alleles = Column(String(255), nullable=False, default="HLA-A*02:01, HLA-A*24:02, HLA-B*07:02")
    somatic_mutations_analyzed_count = Column(Integer, nullable=False, default=45)
    high_affinity_neoepitopes_count = Column(Integer, nullable=False, default=8)
    immunogenicity_score_mean = Column(Float, nullable=False, default=0.86)
    proteasomal_cleavage_efficiency = Column(Float, nullable=False, default=0.92)
    tap_transport_efficiency = Column(Float, nullable=False, default=0.88)
    mrna_vaccine_tier1_candidates_count = Column(Integer, nullable=False, default=3)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    peptide_candidates = relationship("NeoantigenPeptideCandidate", back_populates="study", cascade="all, delete-orphan")
    hla_predictions = relationship("NeoantigenHLABindingPrediction", back_populates="study", cascade="all, delete-orphan")


class NeoantigenPeptideCandidate(Base):
    """Candidate mutated 9-11mer neoantigen peptides."""

    __tablename__ = "neoantigen_peptide_candidates"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("neoantigen_hla_presentation_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    gene_symbol = Column(String(100), nullable=False)
    mutation_syntax = Column(String(100), nullable=False)  # e.g., p.V600E
    wildtype_peptide = Column(String(50), nullable=False)
    mutant_peptide_sequence = Column(String(50), nullable=False)
    peptide_length = Column(Integer, nullable=False, default=9)
    tcr_recognition_probability = Column(Float, nullable=False, default=0.85)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NeoantigenHLAStudy", back_populates="peptide_candidates")


class NeoantigenHLABindingPrediction(Base):
    """HLA allele-specific binding affinity (IC50) and presentation percentile rank."""

    __tablename__ = "neoantigen_hla_binding_predictions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("neoantigen_hla_presentation_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    peptide_sequence = Column(String(50), nullable=False)
    hla_allele = Column(String(100), nullable=False)
    binding_affinity_ic50_nm = Column(Float, nullable=False)
    presentation_percentile_rank = Column(Float, nullable=False)
    stability_half_life_hours = Column(Float, nullable=False)
    is_strong_binder = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NeoantigenHLAStudy", back_populates="hla_predictions")