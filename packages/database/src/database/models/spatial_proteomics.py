"""Multiplexed Spatial Proteomics & Imaging Mass Cytometry Database Models (Phase 102)."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base
from database.models.memory import GUID


class DBSpatialProteomicsExperiment(Base):
    __tablename__ = "spatial_proteomics_experiments"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    sample_name = Column(String(255), nullable=False)
    tissue_origin = Column(String(100), nullable=False)  # e.g., Cutaneous Melanoma, Colorectal Adenocarcinoma
    imaging_modality = Column(String(100), default="Hyperion Imaging Mass Cytometry", nullable=False)  # Hyperion IMC, MIBI-TOF, Akoya PhenoCycler
    total_channels = Column(Integer, default=40, nullable=False)
    total_segmented_cells = Column(Integer, default=24500, nullable=False)
    mean_cellular_density_per_mm2 = Column(Float, default=3200.0, nullable=False)
    immune_infiltration_score = Column(Float, default=78.5, nullable=False)  # 0 to 100
    tumor_stroma_mixing_entropy = Column(Float, default=0.812, nullable=False)
    analysis_metadata = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    marker_channels = relationship("DBChannelMarkerIntensity", back_populates="experiment", cascade="all, delete-orphan")
    neighborhoods = relationship("DBCellularNeighborhoodSpatialMatrix", back_populates="experiment", cascade="all, delete-orphan")


class DBChannelMarkerIntensity(Base):
    __tablename__ = "spatial_marker_channels"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(GUID(), ForeignKey("spatial_proteomics_experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    metal_isotope_tag = Column(String(50), nullable=False)  # 168Er, 175Lu, 141Pr
    antibody_target = Column(String(100), nullable=False)  # CD8a, Pan-Keratin, FoxP3, Ki-67, PD-L1, CD68, SMA
    mean_signal_intensity = Column(Float, nullable=False)
    signal_to_noise_ratio = Column(Float, default=14.2, nullable=False)
    positive_cells_percentage = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    experiment = relationship("DBSpatialProteomicsExperiment", back_populates="marker_channels")


class DBCellularNeighborhoodSpatialMatrix(Base):
    __tablename__ = "spatial_cellular_neighborhoods"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(GUID(), ForeignKey("spatial_proteomics_experiments.id", ondelete="CASCADE"), nullable=False, index=True)
    neighborhood_cluster_name = Column(String(100), nullable=False)  # Cytotoxic Immune Niche, Granulocytic Stroma, Proliferative Tumor Core
    dominant_cell_type = Column(String(100), nullable=False)
    neighbor_cell_count = Column(Integer, nullable=False)
    interaction_enrichment_z_score = Column(Float, default=3.45, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    experiment = relationship("DBSpatialProteomicsExperiment", back_populates="neighborhoods")
