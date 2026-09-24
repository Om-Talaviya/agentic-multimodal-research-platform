"""Phase 155: Multi-Modal Spatial Proteomics & CODEX Single-Cell Multiplexing Models."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBSpatialProteomicsCODEXStudy(Base):
    """High-plex spatial proteomics multiplexed fluorescence imaging study."""

    __tablename__ = "spatial_proteomics_codex_studies"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    tissue_sample_name = Column(String(255), nullable=False)
    organ_tissue_type = Column(String(120), default="Tumor Microenvironment")
    multiplex_panel_size = Column(Integer, default=40, nullable=False)
    single_cells_segmented = Column(Integer, default=0, nullable=False)
    cellular_neighborhoods_count = Column(Integer, default=0, nullable=False)
    mean_signal_to_background = Column(Float, default=0.0)
    immune_infiltration_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    marker_expressions = relationship("DBCODEXProteinMarkerExpression", back_populates="study", cascade="all, delete-orphan")
    neighborhood_phenotypes = relationship("DBSingleCellSpatialNeighborhoodPhenotype", back_populates="study", cascade="all, delete-orphan")


class DBCODEXProteinMarkerExpression(Base):
    """Multiplexed antibody marker signal intensity across spatial channels."""

    __tablename__ = "codex_protein_marker_expressions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("spatial_proteomics_codex_studies.id", ondelete="CASCADE"), nullable=False)
    marker_name = Column(String(64), nullable=False)
    cellular_compartment = Column(String(64), default="Membrane")
    mean_fluorescence_intensity = Column(Float, nullable=False)
    signal_to_noise_ratio = Column(Float, nullable=False)
    positive_cells_percentage = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBSpatialProteomicsCODEXStudy", back_populates="marker_expressions")


class DBSingleCellSpatialNeighborhoodPhenotype(Base):
    """Cellular microenvironment spatial neighborhood composition cluster."""

    __tablename__ = "single_cell_spatial_neighborhood_phenotypes"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    study_id = Column(GUID(), ForeignKey("spatial_proteomics_codex_studies.id", ondelete="CASCADE"), nullable=False)
    neighborhood_cluster_id = Column(Integer, nullable=False)
    neighborhood_name = Column(String(120), nullable=False)
    dominant_cell_type = Column(String(120), nullable=False)
    radius_um = Column(Float, nullable=False)
    cell_density_per_mm2 = Column(Float, nullable=False)
    immunosuppression_index = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    study = relationship("DBSpatialProteomicsCODEXStudy", back_populates="neighborhood_phenotypes")
