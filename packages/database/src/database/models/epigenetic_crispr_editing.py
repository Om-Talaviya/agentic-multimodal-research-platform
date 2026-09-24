"""Phase 159: Epigenetic CRISPR Base/Prime Editing DNA Methylation Models."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBEpigeneticCRISPREditingStudy(Base):
    """Targeted dCas9 epigenetic methylation/demethylation editing study."""

    __tablename__ = "epigenetic_crispr_editing_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    target_locus_name = Column(String(255), nullable=False)
    catalytic_effector = Column(String(120), default="dCas9-DNMT3A-DNMT3L Methyltransferase")
    guide_rna_sequence = Column(String(64), nullable=False)
    targeted_cpg_count = Column(Integer, default=12, nullable=False)
    target_methylation_change_pct = Column(Float, default=0.0)
    transcriptional_repression_log2fc = Column(Float, default=0.0)
    mitotic_memory_retention_days = Column(Float, default=0.0)
    off_target_epimutation_rate_pct = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    cpg_profiles = relationship("DBCpGIslandMethylationProfile", back_populates="study", cascade="all, delete-orphan")
    off_targets = relationship("DBOffTargetEpigeneticEpimutation", back_populates="study", cascade="all, delete-orphan")


class DBCpGIslandMethylationProfile(Base):
    """Specific CpG dinucleotide positional methylation status."""

    __tablename__ = "cpg_island_methylation_profiles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("epigenetic_crispr_editing_studies.id", ondelete="CASCADE"), nullable=False)
    genomic_coordinate_bp = Column(Integer, nullable=False)
    baseline_methylation_pct = Column(Float, nullable=False)
    post_edit_methylation_pct = Column(Float, nullable=False)
    bisulfite_read_depth = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBEpigeneticCRISPREditingStudy", back_populates="cpg_profiles")


class DBOffTargetEpigeneticEpimutation(Base):
    """Off-target locus epigenetic modification surveillance point."""

    __tablename__ = "off_target_epigenetic_epimutations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("epigenetic_crispr_editing_studies.id", ondelete="CASCADE"), nullable=False)
    off_target_locus = Column(String(120), nullable=False)
    mismatch_count = Column(Integer, nullable=False)
    methylation_drift_pct = Column(Float, nullable=False)
    safety_classification = Column(String(64), default="BENIGN")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBEpigeneticCRISPREditingStudy", back_populates="off_targets")
