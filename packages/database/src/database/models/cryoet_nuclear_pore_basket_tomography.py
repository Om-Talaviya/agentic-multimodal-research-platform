"""SQLAlchemy models for Phase 438: Autonomous Cryo-ET In-Situ Nuclear Pore Complex (NPC) Nuclear Basket Dynamic Conformation Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CryoetNuclearPoreBasketStudy(Base):
    """Study record for Autonomous Cryo-ET In-Situ Nuclear Pore Complex (NPC) Nuclear Basket Dynamic Conformation Engine."""

    __tablename__ = "p438_cryoet_nuclear_pore_basket_tomography_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Intact HeLa Cell Nuclear Envelope Vitreous Lamella with 8-Fold NPC Basket")
    analytical_modality = Column(String(100), nullable=False, default="cryoet-npc-basket")
    subtomogram_average_resolution_angstrom = Column(Float, nullable=False, default=4.15)
    basket_dilation_radius_nm = Column(Float, nullable=False, default=26.8)
    fg_nucleoporin_confinement_entropy = Column(Float, nullable=False, default=-14.2)
    transport_receptor_docking_occupancy = Column(Float, nullable=False, default=0.924)
    confidence_score = Column(Float, nullable=False, default=0.99)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CryoetNuclearPoreBasketItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("CryoetNuclearPoreBasketMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class CryoetNuclearPoreBasketItemProfile(Base):
    """Detailed item profile for Autonomous Cryo-ET In-Situ Nuclear Pore Complex (NPC) Nuclear Basket Dynamic Conformation Engine."""

    __tablename__ = "p438_cryoet_nuclear_pore_basket_tomography_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p438_cryoet_nuclear_pore_basket_tomography_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CryoetNuclearPoreBasketStudy", back_populates="item_profiles")


class CryoetNuclearPoreBasketMetricTrace(Base):
    """Metric trace for Autonomous Cryo-ET In-Situ Nuclear Pore Complex (NPC) Nuclear Basket Dynamic Conformation Engine."""

    __tablename__ = "p438_cryoet_nuclear_pore_basket_tomography_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p438_cryoet_nuclear_pore_basket_tomography_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CryoetNuclearPoreBasketStudy", back_populates="metric_traces")
