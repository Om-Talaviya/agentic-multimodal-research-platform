"""SQLAlchemy models for Phase 475: Autonomous Multiplexed Bio-Acoustic Cellular Impedance Flow Cytometry Classifier."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class AcousticImpedanceCytometryStudy(Base):
    """Study record for Autonomous Multiplexed Bio-Acoustic Cellular Impedance Flow Cytometry Classifier."""

    __tablename__ = "p475_acoustic_impedance_cytometry_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="High-Throughput Microfluidic Coplanar Electrode Microchannel with Circulating Tumor Cell Suspensions")
    analytical_modality = Column(String(100), nullable=False, default="acoustic-impedance-cytometry")
    dielectric_membrane_capacitance_uF_per_cm2 = Column(Float, nullable=False, default=1.25)
    cytoplasm_conductivity_S_per_m = Column(Float, nullable=False, default=0.68)
    acoustic_focusing_transit_time_uniformity_cv = Column(Float, nullable=False, default=0.032)
    single_cell_classification_accuracy = Column(Float, nullable=False, default=0.985)
    confidence_score = Column(Float, nullable=False, default=0.992)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("AcousticImpedanceCytometryItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("AcousticImpedanceCytometryMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class AcousticImpedanceCytometryItemProfile(Base):
    """Detailed item profile for Autonomous Multiplexed Bio-Acoustic Cellular Impedance Flow Cytometry Classifier."""

    __tablename__ = "p475_acoustic_impedance_cytometry_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p475_acoustic_impedance_cytometry_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("AcousticImpedanceCytometryStudy", back_populates="item_profiles")


class AcousticImpedanceCytometryMetricTrace(Base):
    """Metric trace for Autonomous Multiplexed Bio-Acoustic Cellular Impedance Flow Cytometry Classifier."""

    __tablename__ = "p475_acoustic_impedance_cytometry_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p475_acoustic_impedance_cytometry_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("AcousticImpedanceCytometryStudy", back_populates="metric_traces")
