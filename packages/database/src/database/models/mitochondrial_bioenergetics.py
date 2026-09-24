"""Mitochondrial OXPHOS Bioenergetics & ROS Dynamics Models (Phase 144)."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import JSON, GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBMitochondrialOXPHOSStudy(Base):
    """Mitochondrial respiration and respiratory state study."""

    __tablename__ = "mitochondrial_oxphos_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    cell_line_or_tissue: str = Column(String(255), nullable=False)
    oxygen_consumption_rate_pmol_min = Column(Float, default=0.0)
    extracellular_acidification_rate = Column(Float, default=0.0)
    respiratory_control_ratio = Column(Float, default=0.0)
    membrane_potential_delta_psi_mv = Column(Float, default=-160.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    etc_complexes = relationship("DBETCComplexActivityRecord", back_populates="study", cascade="all, delete-orphan")
    ros_profiles = relationship("DBROSDynamicsProfile", back_populates="study", cascade="all, delete-orphan")


class DBETCComplexActivityRecord(Base):
    """Electron transport chain complex I-V enzymatic activity."""

    __tablename__ = "etc_complex_activity_records"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("mitochondrial_oxphos_studies.id", ondelete="CASCADE"), nullable=False)
    complex_name = Column(String(50), nullable=False)  # Complex I, II, III, IV, V
    relative_activity_pct = Column(Float, nullable=False)
    proton_pumping_stoichiometry = Column(Float, default=4.0)
    inhibitor_sensitivity = Column(String(100), default="Rotenone")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBMitochondrialOXPHOSStudy", back_populates="etc_complexes")


class DBROSDynamicsProfile(Base):
    """Mitochondrial reactive oxygen species (ROS) and superoxide production."""

    __tablename__ = "ros_dynamics_profiles"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("mitochondrial_oxphos_studies.id", ondelete="CASCADE"), nullable=False)
    superoxide_flux_uM_s = Column(Float, nullable=False)
    h2o2_emission_rate = Column(Float, nullable=False)
    mptp_opening_probability = Column(Float, default=0.05)
    glutathione_redox_ratio = Column(Float, default=50.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBMitochondrialOXPHOSStudy", back_populates="ros_profiles")
