"""SQLAlchemy models for Phase 567: Autonomous Synthetic Protocellular Droplet-Interface-Bilayer (DIB) Ion Channel Network Communicator."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class DropletInterfaceBilayerIonNetworkStudy(Base):
    """Study record for Autonomous Synthetic Protocellular Droplet-Interface-Bilayer (DIB) Ion Channel Network Communicator."""

    __tablename__ = "p567_droplet_interface_bilayer_ion_network_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Aqueous Microdroplets in Oil with Encapsulated Alpha-Hemolysin Ion Channels arranged in a 3D Interfacial Bio-Conductive Lattice")
    analytical_modality = Column(String(100), nullable=False, default="droplet-interface-bilayer-network")
    interfacial_bilayer_electrical_capacitance_uf_cm2 = Column(Float, nullable=False, default=0.72)
    single_channel_conductance_quantization_ps = Column(Float, nullable=False, default=980.0)
    inter_droplet_signal_transmission_speed_mm_s = Column(Float, nullable=False, default=2.8)
    multi_nodal_droplet_network_stability_hours = Column(Float, nullable=False, default=96.0)
    confidence_score = Column(Float, nullable=False, default=0.995)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("DropletInterfaceBilayerIonNetworkItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("DropletInterfaceBilayerIonNetworkMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class DropletInterfaceBilayerIonNetworkItemProfile(Base):
    """Detailed item profile for Autonomous Synthetic Protocellular Droplet-Interface-Bilayer (DIB) Ion Channel Network Communicator."""

    __tablename__ = "p567_droplet_interface_bilayer_ion_network_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p567_droplet_interface_bilayer_ion_network_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DropletInterfaceBilayerIonNetworkStudy", back_populates="item_profiles")


class DropletInterfaceBilayerIonNetworkMetricTrace(Base):
    """Metric trace for Autonomous Synthetic Protocellular Droplet-Interface-Bilayer (DIB) Ion Channel Network Communicator."""

    __tablename__ = "p567_droplet_interface_bilayer_ion_network_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p567_droplet_interface_bilayer_ion_network_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DropletInterfaceBilayerIonNetworkStudy", back_populates="metric_traces")
