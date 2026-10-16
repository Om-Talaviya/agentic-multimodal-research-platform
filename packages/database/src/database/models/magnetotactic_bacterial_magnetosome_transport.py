"""SQLAlchemy models for Phase 551: Autonomous Engineered Magnetotactic Bacterial Magnetosome Nanowire Steering & Drug Cargo Transport Simulator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class MagnetotacticBacterialMagnetosomeTransportStudy(Base):
    """Study record for Autonomous Engineered Magnetotactic Bacterial Magnetosome Nanowire Steering & Drug Cargo Transport Simulator."""

    __tablename__ = "p551_magnetotactic_bacterial_magnetosome_transport_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Engineered Magnetospirillum magneticum AMB-1 expressing Doxorubicin-Loaded Membrane Nanovesicles in Microfluidic Vascular Capillaries")
    analytical_modality = Column(String(100), nullable=False, default="bacterial-magnetosome-transport")
    magnetic_steering_velocity_um_s = Column(Float, nullable=False, default=48.5)
    magnetosome_chain_magnetic_moment_femu = Column(Float, nullable=False, default=12.5)
    tumor_microvascular_extravasation_rate_pct = Column(Float, nullable=False, default=34.2)
    nanocarrier_drug_payload_delivery_ng_ml = Column(Float, nullable=False, default=82.0)
    confidence_score = Column(Float, nullable=False, default=0.995)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("MagnetotacticBacterialMagnetosomeTransportItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("MagnetotacticBacterialMagnetosomeTransportMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class MagnetotacticBacterialMagnetosomeTransportItemProfile(Base):
    """Detailed item profile for Autonomous Engineered Magnetotactic Bacterial Magnetosome Nanowire Steering & Drug Cargo Transport Simulator."""

    __tablename__ = "p551_magnetotactic_bacterial_magnetosome_transport_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p551_magnetotactic_bacterial_magnetosome_transport_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MagnetotacticBacterialMagnetosomeTransportStudy", back_populates="item_profiles")


class MagnetotacticBacterialMagnetosomeTransportMetricTrace(Base):
    """Metric trace for Autonomous Engineered Magnetotactic Bacterial Magnetosome Nanowire Steering & Drug Cargo Transport Simulator."""

    __tablename__ = "p551_magnetotactic_bacterial_magnetosome_transport_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p551_magnetotactic_bacterial_magnetosome_transport_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("MagnetotacticBacterialMagnetosomeTransportStudy", back_populates="metric_traces")
