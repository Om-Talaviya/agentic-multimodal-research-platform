"""SQLAlchemy models for Phase 429: Autonomous Whole-Cell Organelle Contact Site & Membrane Proximity Distance Transformer."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class OrganelleContactSiteProximityStudy(Base):
    """Study record for Autonomous Whole-Cell Organelle Contact Site & Membrane Proximity Distance Transformer."""

    __tablename__ = "p429_organelle_contact_site_proximity_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Focused Ion Beam Scanning Electron Microscopy (FIB-SEM) Whole Cell")
    analytical_modality = Column(String(100), nullable=False, default="organelle-contact-site")
    er_mitochondria_contact_distance_nm = Column(Float, nullable=False, default=14.2)
    contact_site_surface_area_um2 = Column(Float, nullable=False, default=2.85)
    lipid_transfer_flux_rate = Column(Float, nullable=False, default=125.0)
    organelle_tethering_density = Column(Float, nullable=False, default=0.892)
    confidence_score = Column(Float, nullable=False, default=0.99)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("OrganelleContactSiteProximityItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("OrganelleContactSiteProximityMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class OrganelleContactSiteProximityItemProfile(Base):
    """Detailed item profile for Autonomous Whole-Cell Organelle Contact Site & Membrane Proximity Distance Transformer."""

    __tablename__ = "p429_organelle_contact_site_proximity_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p429_organelle_contact_site_proximity_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OrganelleContactSiteProximityStudy", back_populates="item_profiles")


class OrganelleContactSiteProximityMetricTrace(Base):
    """Metric trace for Autonomous Whole-Cell Organelle Contact Site & Membrane Proximity Distance Transformer."""

    __tablename__ = "p429_organelle_contact_site_proximity_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p429_organelle_contact_site_proximity_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("OrganelleContactSiteProximityStudy", back_populates="metric_traces")
