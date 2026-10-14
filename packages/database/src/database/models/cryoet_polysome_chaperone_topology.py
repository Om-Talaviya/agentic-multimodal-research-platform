"""SQLAlchemy models for Phase 481: Autonomous In-Situ Cryo-ET Ribosome Polysome Structural Topology & Nascent Chain Chaperone Coordinator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CryoetPolysomeChaperoneTopologyStudy(Base):
    """Study record for Autonomous In-Situ Cryo-ET Ribosome Polysome Structural Topology & Nascent Chain Chaperone Coordinator."""

    __tablename__ = "p481_cryoet_polysome_chaperone_topology_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Vitrified Mammalian Reticulocyte Cytoplasm with Circular Polysome-Hsp70 Chaperone Ensembles")
    analytical_modality = Column(String(100), nullable=False, default="cryoet-polysome-topology")
    inter_ribosomal_exit_channel_distance_nm = Column(Float, nullable=False, default=16.8)
    polysome_circularity_topology_index = Column(Float, nullable=False, default=0.885)
    chaperone_nascent_chain_occupancy_ratio = Column(Float, nullable=False, default=0.912)
    subtomogram_averaging_resolution_angstrom = Column(Float, nullable=False, default=5.25)
    confidence_score = Column(Float, nullable=False, default=0.993)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CryoetPolysomeChaperoneTopologyItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("CryoetPolysomeChaperoneTopologyMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class CryoetPolysomeChaperoneTopologyItemProfile(Base):
    """Detailed item profile for Autonomous In-Situ Cryo-ET Ribosome Polysome Structural Topology & Nascent Chain Chaperone Coordinator."""

    __tablename__ = "p481_cryoet_polysome_chaperone_topology_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p481_cryoet_polysome_chaperone_topology_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CryoetPolysomeChaperoneTopologyStudy", back_populates="item_profiles")


class CryoetPolysomeChaperoneTopologyMetricTrace(Base):
    """Metric trace for Autonomous In-Situ Cryo-ET Ribosome Polysome Structural Topology & Nascent Chain Chaperone Coordinator."""

    __tablename__ = "p481_cryoet_polysome_chaperone_topology_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p481_cryoet_polysome_chaperone_topology_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CryoetPolysomeChaperoneTopologyStudy", back_populates="metric_traces")
