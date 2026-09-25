"""Epigenetic DNA Methylation Biological Age & Mortality Forecaster Model."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


class DBDNAMethylationClockStudy(Base):
    """Database model for DNA methylation biological clock runs."""

    __tablename__ = "dna_methylation_clock_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_name = Column(String(255), nullable=False, index=True)
    sample_identifier = Column(String(255), nullable=False, default="DONOR-EPIGEN-01")
    tissue_type = Column(String(64), nullable=False, default="whole_blood")
    chronological_age = Column(Float, nullable=False, default=45.0)
    horvath_predicted_age = Column(Float, nullable=False, default=44.2)
    hannum_predicted_age = Column(Float, nullable=False, default=43.8)
    phenoage_predicted_age = Column(Float, nullable=False, default=46.1)
    grimage_mortality_risk_score = Column(Float, nullable=False, default=0.22)
    age_acceleration_delta = Column(Float, nullable=False, default=-0.8)
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

    cpg_markers = relationship(
        "DBCpGIslandMethylationMarker",
        back_populates="study",
        cascade="all, delete-orphan",
        lazy="joined",
    )
    age_metrics = relationship(
        "DBEpigeneticAgeAccelerationMetric",
        back_populates="study",
        cascade="all, delete-orphan",
        lazy="joined",
    )


class DBCpGIslandMethylationMarker(Base):
    """Database model for specific CpG locus beta-values and clock weights."""

    __tablename__ = "cpg_methylation_markers"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("dna_methylation_clock_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    cpg_probe_id = Column(String(64), nullable=False)
    target_gene = Column(String(64), nullable=False)
    chromosome = Column(String(16), nullable=False)
    genomic_coordinate = Column(Integer, nullable=False)
    beta_value = Column(Float, nullable=False)
    clock_weight = Column(Float, nullable=False)
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    study = relationship("DBDNAMethylationClockStudy", back_populates="cpg_markers")


class DBEpigeneticAgeAccelerationMetric(Base):
    """Database model for clock-specific age acceleration & mortality hazard metrics."""

    __tablename__ = "epigenetic_age_metrics"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("dna_methylation_clock_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    clock_algorithm = Column(String(64), nullable=False)
    predicted_epigenetic_age = Column(Float, nullable=False)
    acceleration_residual = Column(Float, nullable=False)
    mortality_hazard_ratio = Column(Float, nullable=False)
    created_at = Column(
        String(64),
        nullable=False,
        default=lambda: datetime.now(UTC).isoformat(),
    )

    study = relationship("DBDNAMethylationClockStudy", back_populates="age_metrics")
