"""SQLAlchemy models for Phase 178: Autonomous ADC DAR Optimization & Aggregation Predictor."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class ADCDAROptStudy(Base):
    """Study record for antibody-drug conjugate DAR profiling and aggregation simulation."""

    __tablename__ = "adc_dar_opt_studies"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    antibody_name = Column(String(255), nullable=False)
    payload_name = Column(String(255), nullable=False)
    linker_type = Column(String(100), nullable=False, default="cleavable_val_cit")
    conjugation_chemistry = Column(String(100), nullable=False, default="cysteine_maleimide")
    target_dar = Column(Float, nullable=False, default=4.0)
    calculated_mean_dar = Column(Float, nullable=False, default=3.85)
    aggregation_propensity_score = Column(Float, nullable=False, default=0.12)
    hydrophobicity_index = Column(Float, nullable=False, default=2.45)
    unconjugated_antibody_pct = Column(Float, nullable=False, default=4.2)
    high_dar_overload_pct = Column(Float, nullable=False, default=6.8)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    species_distributions = relationship("ADCDARSpeciesDistribution", back_populates="study", cascade="all, delete-orphan")
    aggregation_metrics = relationship("ADCDARAggregationMetric", back_populates="study", cascade="all, delete-orphan")


class ADCDARSpeciesDistribution(Base):
    """Individual DAR species fractions (DAR 0 through DAR 8)."""

    __tablename__ = "adc_dar_species_distributions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("adc_dar_opt_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    dar_species = Column(Integer, nullable=False)  # 0, 2, 4, 6, 8 etc.
    molar_fraction = Column(Float, nullable=False)
    retention_time_min = Column(Float, nullable=False)
    mass_shift_da = Column(Float, nullable=False)
    relative_clearance_rate = Column(Float, nullable=False, default=1.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("ADCDAROptStudy", back_populates="species_distributions")


class ADCDARAggregationMetric(Base):
    """Aggregation kinetics and hydrodynamic stability over time."""

    __tablename__ = "adc_dar_aggregation_metrics"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("adc_dar_opt_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    incubation_hours = Column(Float, nullable=False)
    monomer_percentage = Column(Float, nullable=False)
    high_molecular_weight_pct = Column(Float, nullable=False)
    low_molecular_weight_pct = Column(Float, nullable=False)
    turbidity_od350 = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("ADCDAROptStudy", back_populates="aggregation_metrics")
