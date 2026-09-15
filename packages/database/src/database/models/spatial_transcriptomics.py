"""Database models for Spatial Transcriptomics and Tissue Microenvironment (Phase 42)."""
from datetime import datetime, timezone
import uuid
from typing import List, Optional, Dict, Any

from sqlalchemy import String, Float, Integer, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from database.models.memory import GUID, JSONType

class DBSpatialTissueDataset(Base):
    __tablename__ = "spatial_tissue_datasets"

    id: Mapped[str] = mapped_column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True)
    project_id: Mapped[Optional[str]] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    organism: Mapped[str] = mapped_column(String(100), default="Homo sapiens")
    tissue_type: Mapped[str] = mapped_column(String(100), nullable=False)
    technology: Mapped[str] = mapped_column(String(100), default="10x Visium")
    
    total_spots: Mapped[int] = mapped_column(Integer, default=0)
    total_genes: Mapped[int] = mapped_column(Integer, default=0)
    slide_width_um: Mapped[float] = mapped_column(Float, default=6500.0)
    slide_height_um: Mapped[float] = mapped_column(Float, default=6500.0)
    spot_diameter_um: Mapped[float] = mapped_column(Float, default=55.0)
    
    status: Mapped[str] = mapped_column(String(50), default="completed")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    spots: Mapped[List["DBCellSpatialCoordinate"]] = relationship("DBCellSpatialCoordinate", back_populates="dataset", cascade="all, delete-orphan")
    communications: Mapped[List["DBCellCommunicationPair"]] = relationship("DBCellCommunicationPair", back_populates="dataset", cascade="all, delete-orphan")
    domains: Mapped[List["DBSpatialDomain"]] = relationship("DBSpatialDomain", back_populates="dataset", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_spatial_datasets_workspace", "workspace_id"),
        Index("ix_spatial_datasets_tissue", "tissue_type"),
    )

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

    __table_args__ = (
        Index("ix_spatial_coords_dataset", "dataset_id"),
        Index("ix_spatial_coords_xy", "dataset_id", "x_coord", "y_coord"),
        Index("ix_spatial_coords_cluster", "dataset_id", "cluster_id"),
    )

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

    __table_args__ = (
        Index("ix_spatial_comm_dataset", "dataset_id"),
        Index("ix_spatial_comm_pathway", "dataset_id", "pathway_name"),
    )

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

    __table_args__ = (
        Index("ix_spatial_domains_dataset", "dataset_id"),
    )
