"""SQLAlchemy models for Phase 511: Autonomous In-Situ Cryo-ET Nuclear Envelope Lamina Meshwork & Mechanical Rigidity Engine."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from database.connection import Base


def utc_now() -> datetime:
    return datetime.now(UTC)


class CryoetNuclearEnvelopeLaminaMeshworkStudy(Base):
    """Study record for Autonomous In-Situ Cryo-ET Nuclear Envelope Lamina Meshwork & Mechanical Rigidity Engine."""

    __tablename__ = "p511_cryoet_nuclear_envelope_lamina_meshwork_studies"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    target_specimen = Column(String(100), nullable=False, default="Vitrified Fibroblast Nucleus Section with Lamin A/C Filamentous Intermediate Meshwork")
    analytical_modality = Column(String(100), nullable=False, default="cryoet-nuclear-envelope-lamina")
    lamin_filament_diameter_nm = Column(Float, nullable=False, default=3.5)
    orthogonal_meshwork_pore_size_nm = Column(Float, nullable=False, default=48.0)
    nuclear_membrane_elastic_modulus_kPa = Column(Float, nullable=False, default=12.5)
    subtomogram_averaging_fsc_resolution_angstrom = Column(Float, nullable=False, default=6.4)
    confidence_score = Column(Float, nullable=False, default=0.992)
    status = Column(String(50), nullable=False, default="completed")
    parameters = Column(JSON, nullable=True, default=dict)
    summary_report = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    item_profiles = relationship("CryoetNuclearEnvelopeLaminaMeshworkItemProfile", back_populates="study", cascade="all, delete-orphan", lazy="selectin")
    metric_traces = relationship("CryoetNuclearEnvelopeLaminaMeshworkMetricTrace", back_populates="study", cascade="all, delete-orphan", lazy="selectin")


class CryoetNuclearEnvelopeLaminaMeshworkItemProfile(Base):
    """Detailed item profile for Autonomous In-Situ Cryo-ET Nuclear Envelope Lamina Meshwork & Mechanical Rigidity Engine."""

    __tablename__ = "p511_cryoet_nuclear_envelope_lamina_meshwork_item_profiles"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p511_cryoet_nuclear_envelope_lamina_meshwork_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(150), nullable=False)
    profile_category = Column(String(100), nullable=False, default="Analysis Profile")
    quantitative_value = Column(Float, nullable=False)
    log2_fold_change = Column(Float, nullable=False, default=1.5)
    significance_score = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CryoetNuclearEnvelopeLaminaMeshworkStudy", back_populates="item_profiles")


class CryoetNuclearEnvelopeLaminaMeshworkMetricTrace(Base):
    """Metric trace for Autonomous In-Situ Cryo-ET Nuclear Envelope Lamina Meshwork & Mechanical Rigidity Engine."""

    __tablename__ = "p511_cryoet_nuclear_envelope_lamina_meshwork_metric_traces"
    __table_args__ = {"extend_existing": True}

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(PG_UUID(as_uuid=True), ForeignKey("p511_cryoet_nuclear_envelope_lamina_meshwork_studies.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_dimension = Column(String(100), nullable=False)
    observed_value = Column(Float, nullable=False)
    z_score = Column(Float, nullable=False, default=0.0)
    p_value = Column(Float, nullable=False, default=0.05)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("CryoetNuclearEnvelopeLaminaMeshworkStudy", back_populates="metric_traces")
