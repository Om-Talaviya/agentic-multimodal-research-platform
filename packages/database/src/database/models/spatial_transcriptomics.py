"""Spatial Transcriptomics & Microenvironment Database Models (Phases 42 & 94)."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, String, Float, Integer, JSON, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database.connection import Base
from database.models.memory import GUID

# Support legacy JSON type fallback
JSONType = JSON


class DBSpatialTissueDataset(Base):
    __tablename__ = "spatial_tissue_datasets"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id: Mapped[Optional[str]] = mapped_column(GUID(), nullable=True, index=True)
    project_id: Mapped[Optional[str]] = mapped_column(GUID(), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tissue_type: Mapped[str] = mapped_column(String(100), nullable=False)
    organism: Mapped[str] = mapped_column(String(100), default="Homo sapiens")
    technology: Mapped[str] = mapped_column(String(100), default="10x Visium")
    slide_width_um: Mapped[float] = mapped_column(Float, default=6500.0)
    slide_height_um: Mapped[float] = mapped_column(Float, default=6500.0)
    spot_diameter_um: Mapped[float] = mapped_column(Float, default=55.0)
    total_spots: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="completed")
    meta_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    spots: Mapped[List["DBCellSpatialCoordinate"]] = relationship("DBCellSpatialCoordinate", back_populates="dataset", cascade="all, delete-orphan")
    communications: Mapped[List["DBCellCommunicationPair"]] = relationship("DBCellCommunicationPair", back_populates="dataset", cascade="all, delete-orphan")
    domains: Mapped[List["DBSpatialDomain"]] = relationship("DBSpatialDomain", back_populates="dataset", cascade="all, delete-orphan")


class DBCellSpatialCoordinate(Base):
    __tablename__ = "spatial_cell_coordinates"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id: Mapped[str] = mapped_column(GUID(), ForeignKey("spatial_tissue_datasets.id", ondelete="CASCADE"), nullable=False)
    
    spot_barcode: Mapped[str] = mapped_column(String(100), nullable=False)
    x_coord: Mapped[float] = mapped_column(Float, nullable=False)
    y_coord: Mapped[float] = mapped_column(Float, nullable=False)
    z_coord: Mapped[float] = mapped_column(Float, default=0.0)
    
    cluster_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cluster_name: Mapped[str] = mapped_column(String(100), default="Unassigned")
    cell_type_annotation: Mapped[str] = mapped_column(String(100), default="Unknown")
    
    total_counts: Mapped[int] = mapped_column(Integer, default=1000)
    n_genes_detected: Mapped[int] = mapped_column(Integer, default=500)
    spatial_domain_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tumor_proximity_score: Mapped[float] = mapped_column(Float, default=0.0)
    
    meta_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    dataset: Mapped["DBSpatialTissueDataset"] = relationship("DBSpatialTissueDataset", back_populates="spots")


class DBCellCommunicationPair(Base):
    __tablename__ = "spatial_cell_communications"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id: Mapped[str] = mapped_column(GUID(), ForeignKey("spatial_tissue_datasets.id", ondelete="CASCADE"), nullable=False)
    
    pathway_name: Mapped[str] = mapped_column(String(100), nullable=False)
    ligand_gene: Mapped[str] = mapped_column(String(50), nullable=False)
    receptor_gene: Mapped[str] = mapped_column(String(50), nullable=False)
    
    source_cluster: Mapped[str] = mapped_column(String(100), nullable=False)
    target_cluster: Mapped[str] = mapped_column(String(100), nullable=False)
    
    communication_score: Mapped[float] = mapped_column(Float, nullable=False)
    p_value: Mapped[float] = mapped_column(Float, default=0.001)
    interaction_distance_um: Mapped[float] = mapped_column(Float, default=120.0)
    is_spatially_constrained: Mapped[bool] = mapped_column(default=True)
    
    meta_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    dataset: Mapped["DBSpatialTissueDataset"] = relationship("DBSpatialTissueDataset", back_populates="communications")


class DBSpatialDomain(Base):
    __tablename__ = "spatial_tissue_domains"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id: Mapped[str] = mapped_column(GUID(), ForeignKey("spatial_tissue_datasets.id", ondelete="CASCADE"), nullable=False)
    
    domain_name: Mapped[str] = mapped_column(String(100), nullable=False)
    domain_type: Mapped[str] = mapped_column(String(100), default="tumor_stroma")
    color_hex: Mapped[str] = mapped_column(String(20), default="#3b82f6")
    
    spot_count: Mapped[int] = mapped_column(Integer, default=0)
    area_percentage: Mapped[float] = mapped_column(Float, default=0.0)
    top_marker_genes: Mapped[Optional[List[str]]] = mapped_column(JSONType, nullable=True)
    boundary_polygon: Mapped[Optional[List[Dict[str, float]]]] = mapped_column(JSONType, nullable=True)
    
    meta_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    dataset: Mapped["DBSpatialTissueDataset"] = relationship("DBSpatialTissueDataset", back_populates="domains")


# --- Phase 94 Models: Deconvolution & Cellular Niche Profiling ---

class DBSpatialTranscriptomicsSlice(Base):
    __tablename__ = "spatial_transcriptomics_slices"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(GUID(), nullable=False, index=True)
    sample_name = Column(String(255), nullable=False)
    tissue_type = Column(String(100), nullable=False)  # e.g., HER2+ Breast Cancer, Glioblastoma
    platform = Column(String(100), default="10x Visium HD", nullable=False)  # 10x Visium, Xenium, Stereo-seq
    total_spots = Column(Integer, default=4992, nullable=False)
    median_genes_per_spot = Column(Float, default=3200.0, nullable=False)
    deconvolution_algorithm = Column(String(100), default="Spatial-Bayes-Deconv", nullable=False)
    spatial_entropy_score = Column(Float, default=0.74, nullable=False)
    analysis_metadata = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    cell_proportions = relationship("DBCellTypeProportion", back_populates="slice", cascade="all, delete-orphan")
    ligand_receptors = relationship("DBSpatialLigandReceptor", back_populates="slice", cascade="all, delete-orphan")


class DBCellTypeProportion(Base):
    __tablename__ = "spatial_cell_proportions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    slice_id = Column(GUID(), ForeignKey("spatial_transcriptomics_slices.id", ondelete="CASCADE"), nullable=False, index=True)
    cell_type = Column(String(100), nullable=False)  # CD8+ T Cell, Cancer Associated Fibroblast, Malignant Epithelial
    mean_abundance_fraction = Column(Float, nullable=False)  # 0.0 to 1.0
    spatial_enrichment_zone = Column(String(100), default="Tumor Core", nullable=False)  # Stroma, Invasive Margin, Core
    marker_genes = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    slice = relationship("DBSpatialTranscriptomicsSlice", back_populates="cell_proportions")


class DBSpatialLigandReceptor(Base):
    __tablename__ = "spatial_ligand_receptors"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    slice_id = Column(GUID(), ForeignKey("spatial_transcriptomics_slices.id", ondelete="CASCADE"), nullable=False, index=True)
    ligand_gene = Column(String(50), nullable=False)  # CXCL12, VEGFA, TGFB1
    receptor_gene = Column(String(50), nullable=False)  # CXCR4, VEGFR2, TGFBR2
    sender_cell_type = Column(String(100), nullable=False)
    receiver_cell_type = Column(String(100), nullable=False)
    communication_score = Column(Float, default=0.85, nullable=False)  # 0.0 to 1.0
    p_value = Column(Float, default=0.001, nullable=False)
    spatial_colocalization_score = Column(Float, default=0.78, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    slice = relationship("DBSpatialTranscriptomicsSlice", back_populates="ligand_receptors")
