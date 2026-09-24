"""Spatial RNA Velocity & Morphogenesis Models (Phase 146)."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import JSON, GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBSpatialRNAVelocityStudy(Base):
    """Spatial RNA velocity and spliced/unspliced kinetics study."""

    __tablename__ = "spatial_rna_velocity_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    tissue_sample_name = Column(String(255), nullable=False)
    developmental_stage = Column(String(100), nullable=False)
    spot_count = Column(Integer, default=0, nullable=False)
    mean_velocity_magnitude = Column(Float, default=0.0)
    coherence_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    vector_spots = relationship("DBVelocityVectorFieldSpot", back_populates="study", cascade="all, delete-orphan")
    streamlines = relationship("DBMorphogenesisStreamline", back_populates="study", cascade="all, delete-orphan")


class DBVelocityVectorFieldSpot(Base):
    """2D spatial coordinates and directional velocity vector."""

    __tablename__ = "velocity_vector_field_spots"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("spatial_rna_velocity_studies.id", ondelete="CASCADE"), nullable=False)
    spot_index = Column(Integer, nullable=False)
    x_coord_um = Column(Float, nullable=False)
    y_coord_um = Column(Float, nullable=False)
    vx_vector = Column(Float, nullable=False)
    vy_vector = Column(Float, nullable=False)
    cell_type_annotation = Column(String(100), default="Progenitor")
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBSpatialRNAVelocityStudy", back_populates="vector_spots")


class DBMorphogenesisStreamline(Base):
    """Continuous integration trajectory representing cell lineage flux."""

    __tablename__ = "morphogenesis_streamlines"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("spatial_rna_velocity_studies.id", ondelete="CASCADE"), nullable=False)
    streamline_id = Column(String(100), nullable=False)
    origin_cell_state = Column(String(100), nullable=False)
    terminal_cell_state = Column(String(100), nullable=False)
    pseudotime_length = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBSpatialRNAVelocityStudy", back_populates="streamlines")
