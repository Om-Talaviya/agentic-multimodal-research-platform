"""SQLAlchemy models for Phase 182: Gut Microbiome-Host Co-Metabolism & SCFA Dynamics Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MicrobiomeMetabolomicsStudy(Base):
    """Study record for gut microbiome taxonomic composition and host-microbe co-metabolic flux."""

    __tablename__ = "microbiome_metabolomics_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    cohort_sample_id = Column(String(100), nullable=False)
    dietary_fiber_intake_g_day = Column(Float, nullable=False, default=32.0)
    firmicutes_bacteroidetes_ratio = Column(Float, nullable=False, default=1.85)
    total_scfa_concentration_mm = Column(Float, nullable=False, default=85.4)
    butyrate_acetate_propionate_ratio = Column(String(50), nullable=False, default="60:25:15")
    gut_barrier_integrity_score = Column(Float, nullable=False, default=0.91)
    secondary_bile_acid_conversion_rate = Column(Float, nullable=False, default=0.74)
    shannon_diversity_index = Column(Float, nullable=False, default=3.82)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    taxa_abundances = relationship("MicrobiomeTaxaAbundance", back_populates="study", cascade="all, delete-orphan")
    scfa_kinetics = relationship("MicrobiomeSCFAKinetics", back_populates="study", cascade="all, delete-orphan")


class MicrobiomeTaxaAbundance(Base):
    """Relative taxonomic abundance of key functional bacterial clades."""

    __tablename__ = "microbiome_taxa_abundances"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("microbiome_metabolomics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    taxon_name = Column(String(150), nullable=False)  # e.g., Faecalibacterium prausnitzii
    phylum = Column(String(100), nullable=False)
    relative_abundance_pct = Column(Float, nullable=False)
    butyrate_synthesis_pathway = Column(String(100), nullable=False, default="butyryl-CoA:acetate CoA-transferase")
    mucosal_adherence_index = Column(Float, nullable=False, default=0.88)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MicrobiomeMetabolomicsStudy", back_populates="taxa_abundances")


class MicrobiomeSCFAKinetics(Base):
    """Metabolite flux rates across intestinal lumen into portal circulation."""

    __tablename__ = "microbiome_scfa_kinetics"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("microbiome_metabolomics_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metabolite_name = Column(String(100), nullable=False)  # Butyrate, Acetate, Propionate, TMAO
    lumen_concentration_mm = Column(Float, nullable=False)
    portal_vein_absorption_rate = Column(Float, nullable=False)
    anti_inflammatory_index = Column(Float, nullable=False)
    gpr41_43_agonist_potency = Column(Float, nullable=False, default=0.85)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MicrobiomeMetabolomicsStudy", back_populates="scfa_kinetics")