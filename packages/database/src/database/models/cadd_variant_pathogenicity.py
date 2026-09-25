"""CADD & In-Silico Variant Pathogenicity Ranker Model."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


class DBCADDVariantStudy(Base):
    """Database model for CADD variant pathogenicity scoring studies."""

    __tablename__ = "cadd_variant_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_name = Column(String(255), nullable=False, index=True)
    genome_build = Column(String(32), nullable=False, default="GRCh38")
    target_gene = Column(String(64), nullable=False, default="TP53")
    variant_count = Column(Integer, nullable=False, default=5)
    mean_phred_score = Column(Float, nullable=False, default=26.4)
    deleterious_variant_count = Column(Integer, nullable=False, default=3)
    summary_metrics = Column(JSON, nullable=True)
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )
    updated_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    variants = relationship(
        "DBCADDSNPScore",
        back_populates="study",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    ensemble_scores = relationship(
        "DBPathogenicityEnsembleScore",
        back_populates="study",
        cascade="all, delete-orphan",
        lazy="joined",
    )


class DBCADDSNPScore(Base):
    """Database model for individual SNV/Indel CADD raw and PHRED scores."""

    __tablename__ = "cadd_snp_scores"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("cadd_variant_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    chromosome = Column(String(16), nullable=False)
    position = Column(Integer, nullable=False)
    reference_allele = Column(String(16), nullable=False)
    alternate_allele = Column(String(16), nullable=False)
    hgvs_c = Column(String(128), nullable=False)
    raw_score = Column(Float, nullable=False)
    phred_score = Column(Float, nullable=False)
    gerp_score = Column(Float, nullable=False)
    phylop_score = Column(Float, nullable=False)
    pathogenicity_verdict = Column(String(64), nullable=False, default="likely_deleterious")
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    study = relationship("DBCADDVariantStudy", back_populates="variants")


class DBPathogenicityEnsembleScore(Base):
    """Database model for multi-algorithm ensemble pathogenicity rankings."""

    __tablename__ = "pathogenicity_ensemble_scores"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("cadd_variant_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    algorithm_name = Column(String(64), nullable=False)
    concordance_rate = Column(Float, nullable=False)
    high_impact_flag = Column(String(32), nullable=False, default="PASS")
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    study = relationship("DBCADDVariantStudy", back_populates="ensemble_scores")
