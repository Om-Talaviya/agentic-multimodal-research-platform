"""SQLAlchemy models for Phase 360: Autonomous Proteome-Wide Native Mass Spectrometry (Native MS) Non-Covalent Complex Stoichiometry Resolver."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class NativeMsComplexStoichiometryStudy(Base):
    """Study record for Resolves intact gas-phase quaternary oligomeric states, protein-lipid-ligand non-covalent binding stoichiometries, and collision-induced dissociation (CID) subcomplex topologies from ultra-high resolution Orbitrap MS spectra.."""

    __tablename__ = "p360_native_ms_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Human Patient Cohort Sample")
    analytical_modality = Column(String(100), nullable=False, default="native-ms-complex-stoichiometry")
    quaternary_mass_determination_accuracy_ppm = Column(Float, nullable=False, default=12.0)
    charge_state_deconvolution_confidence_score = Column(Float, nullable=False, default=99.1)
    confidence_score = Column(Float, nullable=False, default=0.985)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("NativeMsComplexStoichiometryItemProfile", back_populates="study", cascade="all, delete-orphan")
    metric_traces = relationship("NativeMsComplexStoichiometryMetricTrace", back_populates="study", cascade="all, delete-orphan")


class NativeMsComplexStoichiometryItemProfile(Base):
    """Detailed item profile."""

    __tablename__ = "p360_native_ms_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p360_native_ms_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Primary Target")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NativeMsComplexStoichiometryStudy", back_populates="item_profiles")


class NativeMsComplexStoichiometryMetricTrace(Base):
    """Longitudinal and dimensional metric trace."""

    __tablename__ = "p360_native_ms_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p360_native_ms_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=2.1)
    p_value = Column(Float, nullable=False, default=0.001)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("NativeMsComplexStoichiometryStudy", back_populates="metric_traces")
