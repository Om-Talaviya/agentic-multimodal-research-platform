"""
SQLAlchemy Models for Phase 162: Spatial Transcriptomics Microdissection & Subcellular Spot Deconvolution Engine.
"""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey
from database.connection import Base
from database.models.memory import GUID
from sqlalchemy.orm import relationship


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBSpatialMicrodissectionSession(Base):
    __tablename__ = "spatial_microdissection_sessions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    project_id = Column(GUID(), nullable=True, index=True)
    sample_name = Column(String(255), nullable=False)
    tissue_type = Column(String(255), nullable=False)
    total_spots_analyzed = Column(Integer, default=0)
    subcellular_resolution_nm = Column(Float, default=100.0)
    deconvolution_algorithm = Column(String(100), default="Subcellular-NMF-Bayesian")
    mean_cell_type_entropy = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utc_now)

    deconvolutions = relationship(
        "DBSubcellularSpotDeconvolution",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    niche_boundaries = relationship(
        "DBCellularNicheBoundary",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class DBSubcellularSpotDeconvolution(Base):
    __tablename__ = "subcellular_spot_deconvolutions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    session_id = Column(GUID(), ForeignKey("spatial_microdissection_sessions.id"), nullable=False, index=True)
    spot_index = Column(Integer, nullable=False)
    spatial_x_coord = Column(Float, nullable=False)
    spatial_y_coord = Column(Float, nullable=False)
    dominant_cell_type = Column(String(100), nullable=False)
    dominant_cell_proportion = Column(Float, nullable=False)
    cell_type_composition_json = Column(JSON, nullable=False)
    rna_transcripts_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)

    session = relationship("DBSpatialMicrodissectionSession", back_populates="deconvolutions")


class DBCellularNicheBoundary(Base):
    __tablename__ = "cellular_niche_boundaries"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    session_id = Column(GUID(), ForeignKey("spatial_microdissection_sessions.id"), nullable=False, index=True)
    niche_name = Column(String(100), nullable=False)
    boundary_polygon_json = Column(JSON, nullable=False)
    niche_cellularity_score = Column(Float, default=0.0)
    tumor_immune_interface_distance_um = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utc_now)

    session = relationship("DBSpatialMicrodissectionSession", back_populates="niche_boundaries")
