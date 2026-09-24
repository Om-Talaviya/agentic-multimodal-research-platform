"""
SQLAlchemy Models for Phase 166: Micro-Crystal Electron Diffraction (MicroED) Structural Engine.
"""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey
from database.connection import Base
from database.models.memory import GUID
from sqlalchemy.orm import relationship


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBMicroEDExperiment(Base):
    __tablename__ = "microed_experiments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID(), nullable=True, index=True)
    sample_name = Column(String(255), nullable=False)
    crystal_system = Column(String(100), default="Orthorhombic P212121")
    electron_voltage_kv = Column(Float, default=200.0)
    total_rotation_range_degrees = Column(Float, default=120.0)
    resolution_limit_angstrom = Column(Float, nullable=False)
    completeness_percent = Column(Float, nullable=False)
    r_work = Column(Float, nullable=False)
    r_free = Column(Float, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    frames = relationship(
        "DBMicroEDDiffractionFrame",
        back_populates="experiment",
        cascade="all, delete-orphan",
    )
    refinements = relationship(
        "DBMicroEDAtomicRefinement",
        back_populates="experiment",
        cascade="all, delete-orphan",
    )


class DBMicroEDDiffractionFrame(Base):
    __tablename__ = "microed_diffraction_frames"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(GUID(), ForeignKey("microed_experiments.id"), nullable=False, index=True)
    frame_number = Column(Integer, nullable=False)
    tilt_angle_degrees = Column(Float, nullable=False)
    observed_reflections_count = Column(Integer, nullable=False)
    mean_intensity_sigma_ratio = Column(Float, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    experiment = relationship("DBMicroEDExperiment", back_populates="frames")


class DBMicroEDAtomicRefinement(Base):
    __tablename__ = "microed_atomic_refinements"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(GUID(), ForeignKey("microed_experiments.id"), nullable=False, index=True)
    refinement_cycle = Column(Integer, nullable=False)
    ramachandran_favored_percent = Column(Float, nullable=False)
    clashscore = Column(Float, default=1.2)
    electrostatic_potential_peak_density = Column(Float, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    experiment = relationship("DBMicroEDExperiment", back_populates="refinements")
