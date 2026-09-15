"""Autonomous Multi-Omics & Single-Cell Transcriptomics Database Models (Phase 41)."""

import uuid
from datetime import UTC, datetime
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base
from database.models.memory import GUID, JSONType


class DBSingleCellDataset(Base):
    """Master single-cell transcriptomics and multi-omics dataset specification."""

    __tablename__ = "single_cell_datasets"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True, index=True)
    project_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)

    dataset_title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    organism: Mapped[str] = mapped_column(String(100), nullable=False, default="Homo sapiens")
    tissue: Mapped[str] = mapped_column(String(100), nullable=False, default="Liver")
    sequencing_platform: Mapped[str] = mapped_column(String(100), nullable=False, default="10x Chromium Next GEM 3' v3.1")
    total_cells: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_genes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    clustering_resolution: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    metadata_json: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    clusters: Mapped[list["DBCellCluster"]] = relationship("DBCellCluster", back_populates="dataset", cascade="all, delete-orphan", lazy="selectin")
    cell_coordinates: Mapped[list["DBCellCoordinate"]] = relationship("DBCellCoordinate", back_populates="dataset", cascade="all, delete-orphan", lazy="selectin")
    differential_genes: Mapped[list["DBDifferentialGene"]] = relationship("DBDifferentialGene", back_populates="dataset", cascade="all, delete-orphan", lazy="selectin")
    pathway_enrichments: Mapped[list["DBPathwayEnrichment"]] = relationship("DBPathwayEnrichment", back_populates="dataset", cascade="all, delete-orphan", lazy="selectin")


class DBCellCluster(Base):
    """Identified cell subpopulation / cell type cluster from graph community clustering."""

    __tablename__ = "single_cell_clusters"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    dataset_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("single_cell_datasets.id", ondelete="CASCADE"), nullable=False, index=True)

    cluster_index: Mapped[int] = mapped_column(Integer, nullable=False)
    cell_type_annotation: Mapped[str] = mapped_column(String(100), nullable=False)
    cell_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    percentage_of_total: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    top_markers_json: Mapped[list] = mapped_column(JSONType, nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    dataset: Mapped["DBSingleCellDataset"] = relationship("DBSingleCellDataset", back_populates="clusters")


class DBCellCoordinate(Base):
    """2D dimensional reduction coordinates (UMAP/t-SNE) and developmental pseudotime per cell."""

    __tablename__ = "single_cell_coordinates"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    dataset_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("single_cell_datasets.id", ondelete="CASCADE"), nullable=False, index=True)

    cell_barcode: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    cluster_index: Mapped[int] = mapped_column(Integer, nullable=False)
    umap_x: Mapped[float] = mapped_column(Float, nullable=False)
    umap_y: Mapped[float] = mapped_column(Float, nullable=False)
    tsne_x: Mapped[float] = mapped_column(Float, nullable=False)
    tsne_y: Mapped[float] = mapped_column(Float, nullable=False)
    pseudotime_value: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cell_type_annotation: Mapped[str] = mapped_column(String(100), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    dataset: Mapped["DBSingleCellDataset"] = relationship("DBSingleCellDataset", back_populates="cell_coordinates")


class DBDifferentialGene(Base):
    """Cluster-specific differential expression marker gene statistics (Wilcoxon rank-sum)."""

    __tablename__ = "single_cell_differential_genes"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    dataset_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("single_cell_datasets.id", ondelete="CASCADE"), nullable=False, index=True)

    cluster_index: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    gene_symbol: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    log2_fold_change: Mapped[float] = mapped_column(Float, nullable=False)
    p_value: Mapped[float] = mapped_column(Float, nullable=False)
    p_val_adj: Mapped[float] = mapped_column(Float, nullable=False)
    pct_in_cluster: Mapped[float] = mapped_column(Float, nullable=False)
    pct_out_of_cluster: Mapped[float] = mapped_column(Float, nullable=False)
    is_significant: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    dataset: Mapped["DBSingleCellDataset"] = relationship("DBSingleCellDataset", back_populates="differential_genes")


class DBPathwayEnrichment(Base):
    """Gene Set Enrichment Analysis (GSEA) pathway ranking per cell cluster."""

    __tablename__ = "single_cell_pathway_enrichments"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    dataset_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("single_cell_datasets.id", ondelete="CASCADE"), nullable=False, index=True)

    cluster_index: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    pathway_name: Mapped[str] = mapped_column(String(200), nullable=False)
    database_source: Mapped[str] = mapped_column(String(50), nullable=False, default="KEGG")
    normalized_enrichment_score: Mapped[float] = mapped_column(Float, nullable=False)
    p_val_adj: Mapped[float] = mapped_column(Float, nullable=False)
    leading_edge_genes_json: Mapped[list] = mapped_column(JSONType, nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    dataset: Mapped["DBSingleCellDataset"] = relationship("DBSingleCellDataset", back_populates="pathway_enrichments")
