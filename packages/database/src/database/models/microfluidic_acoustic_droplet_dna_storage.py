"""SQLAlchemy models for Phase 545: Autonomous Microfluidic High-Density Acoustic Droplet Synthetic DNA Digital Archival Writer & Reader."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MicrofluidicAcousticDropletDnaStorageStudy(Base):
    """Study record for Autonomous Microfluidic High-Density Acoustic Droplet Synthetic DNA Digital Archival Writer & Reader."""

    __tablename__ = "p545_microfluidic_acoustic_droplet_dna_storage_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Acoustic Ejection Picoliter Well Plate containing Encoded 100-Mbyte Synthetic Oligo Pool with RS ECC")
    analytical_modality = Column(String(100), nullable=False, default="acoustic-droplet-dna-archival")
    dna_archival_data_density_petabytes_per_gram = Column(Float, nullable=False, default=215.0)
    acoustic_droplet_dispensing_throughput_khz = Column(Float, nullable=False, default=15.0)
    reed_solomon_error_correction_recovery_pct = Column(Float, nullable=False, default=100.0)
    per_base_synthesis_accuracy_pct = Column(Float, nullable=False, default=99.92)
    confidence_score = Column(Float, nullable=False, default=0.998)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MicrofluidicAcousticDropletDnaStorageItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MicrofluidicAcousticDropletDnaStorageMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MicrofluidicAcousticDropletDnaStorageItemProfile(Base):
    """Detailed item profile for Autonomous Microfluidic High-Density Acoustic Droplet Synthetic DNA Digital Archival Writer & Reader."""

    __tablename__ = "p545_microfluidic_acoustic_droplet_dna_storage_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p545_microfluidic_acoustic_droplet_dna_storage_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MicrofluidicAcousticDropletDnaStorageStudy", back_populates="item_profiles")


class MicrofluidicAcousticDropletDnaStorageMetricTrace(Base):
    """Metric trace for Autonomous Microfluidic High-Density Acoustic Droplet Synthetic DNA Digital Archival Writer & Reader."""

    __tablename__ = "p545_microfluidic_acoustic_droplet_dna_storage_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p545_microfluidic_acoustic_droplet_dna_storage_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MicrofluidicAcousticDropletDnaStorageStudy", back_populates="metric_traces")
