"""Autonomous Multi-Omics & Single-Cell Transcriptomics Repository (Phase 41)."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.single_cell import (
    DBCellCluster,
    DBCellCoordinate,
    DBDifferentialGene,
    DBPathwayEnrichment,
    DBSingleCellDataset,
)
from shared.logging import get_logger

logger = get_logger(__name__)


class SingleCellRepository:
    """Async repository for scRNA-seq datasets, clusters, cell coordinates, marker genes, and GSEA pathways."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_dataset(
        self,
        user_id: uuid.UUID | str,
        dataset_title: str,
        organism: str = "Homo sapiens",
        tissue: str = "Liver",
        sequencing_platform: str = "10x Chromium Next GEM 3' v3.1",
        total_cells: int = 0,
        total_genes: int = 0,
        clustering_resolution: float = 0.5,
        metadata_json: Optional[Dict[str, Any]] = None,
        workspace_id: Optional[uuid.UUID | str] = None,
        project_id: Optional[uuid.UUID | str] = None,
    ) -> DBSingleCellDataset:
        """Create and persist a master single-cell dataset."""
        dataset = DBSingleCellDataset(
            id=uuid.uuid4(),
            user_id=user_id,
            workspace_id=workspace_id,
            project_id=project_id,
            dataset_title=dataset_title.strip(),
            organism=organism.strip(),
            tissue=tissue.strip(),
            sequencing_platform=sequencing_platform.strip(),
            total_cells=total_cells,
            total_genes=total_genes,
            clustering_resolution=clustering_resolution,
            metadata_json=metadata_json or {},
        )
        self._session.add(dataset)
        await self._session.flush()
        logger.info(
            "single_cell_dataset_created",
            dataset_id=str(dataset.id),
            title=dataset.dataset_title,
            cells=dataset.total_cells,
        )
        return dataset

    async def get_dataset(self, dataset_id: uuid.UUID | str) -> Optional[DBSingleCellDataset]:
        """Fetch single-cell dataset with clusters, marker genes, and pathway enrichments."""
        stmt = (
            select(DBSingleCellDataset)
            .where(DBSingleCellDataset.id == dataset_id)
            .options(
                selectinload(DBSingleCellDataset.clusters),
                selectinload(DBSingleCellDataset.differential_genes),
                selectinload(DBSingleCellDataset.pathway_enrichments),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_datasets(
        self,
        user_id: Optional[uuid.UUID | str] = None,
        workspace_id: Optional[uuid.UUID | str] = None,
        project_id: Optional[uuid.UUID | str] = None,
        tissue: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBSingleCellDataset]:
        """List single-cell datasets with optional filtering."""
        stmt = select(DBSingleCellDataset).options(selectinload(DBSingleCellDataset.clusters))

        if user_id:
            stmt = stmt.where(DBSingleCellDataset.user_id == user_id)
        if workspace_id:
            stmt = stmt.where(DBSingleCellDataset.workspace_id == workspace_id)
        if project_id:
            stmt = stmt.where(DBSingleCellDataset.project_id == project_id)
        if tissue:
            stmt = stmt.where(DBSingleCellDataset.tissue.ilike(f"%{tissue}%"))

        stmt = stmt.order_by(desc(DBSingleCellDataset.created_at)).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def add_clusters(
        self,
        dataset_id: uuid.UUID | str,
        clusters_data: List[Dict[str, Any]],
    ) -> List[DBCellCluster]:
        """Add cell cluster annotations to dataset."""
        created: List[DBCellCluster] = []
        for c in clusters_data:
            cluster = DBCellCluster(
                id=c.get("id") or uuid.uuid4(),
                dataset_id=dataset_id,
                cluster_index=c["cluster_index"],
                cell_type_annotation=c["cell_type_annotation"],
                cell_count=c.get("cell_count", 0),
                percentage_of_total=c.get("percentage_of_total", 0.0),
                top_markers_json=c.get("top_markers_json", []),
            )
            self._session.add(cluster)
            created.append(cluster)

        await self._session.flush()
        return created

    async def add_cell_coordinates(
        self,
        dataset_id: uuid.UUID | str,
        coordinates_data: List[Dict[str, Any]],
    ) -> List[DBCellCoordinate]:
        """Persist 2D UMAP/t-SNE coordinates and pseudotime values for single cells."""
        created: List[DBCellCoordinate] = []
        for coord in coordinates_data:
            cell = DBCellCoordinate(
                id=uuid.uuid4(),
                dataset_id=dataset_id,
                cell_barcode=coord["cell_barcode"],
                cluster_index=coord["cluster_index"],
                umap_x=coord["umap_x"],
                umap_y=coord["umap_y"],
                tsne_x=coord.get("tsne_x", coord["umap_x"] * 1.1),
                tsne_y=coord.get("tsne_y", coord["umap_y"] * 1.1),
                pseudotime_value=coord.get("pseudotime_value", 0.0),
                cell_type_annotation=coord.get("cell_type_annotation", "Unknown"),
            )
            self._session.add(cell)
            created.append(cell)

        await self._session.flush()
        return created

    async def add_differential_genes(
        self,
        dataset_id: uuid.UUID | str,
        genes_data: List[Dict[str, Any]],
    ) -> List[DBDifferentialGene]:
        """Persist differential marker gene expression statistics."""
        created: List[DBDifferentialGene] = []
        for g in genes_data:
            gene = DBDifferentialGene(
                id=uuid.uuid4(),
                dataset_id=dataset_id,
                cluster_index=g["cluster_index"],
                gene_symbol=g["gene_symbol"],
                log2_fold_change=g["log2_fold_change"],
                p_value=g.get("p_value", 1e-12),
                p_val_adj=g.get("p_val_adj", 1e-10),
                pct_in_cluster=g.get("pct_in_cluster", 0.85),
                pct_out_of_cluster=g.get("pct_out_of_cluster", 0.15),
                is_significant=g.get("is_significant", True),
            )
            self._session.add(gene)
            created.append(gene)

        await self._session.flush()
        return created

    async def add_pathway_enrichments(
        self,
        dataset_id: uuid.UUID | str,
        pathways_data: List[Dict[str, Any]],
    ) -> List[DBPathwayEnrichment]:
        """Persist GSEA pathway enrichment rankings."""
        created: List[DBPathwayEnrichment] = []
        for p in pathways_data:
            pathway = DBPathwayEnrichment(
                id=uuid.uuid4(),
                dataset_id=dataset_id,
                cluster_index=p["cluster_index"],
                pathway_name=p["pathway_name"],
                database_source=p.get("database_source", "KEGG"),
                normalized_enrichment_score=p["normalized_enrichment_score"],
                p_val_adj=p.get("p_val_adj", 0.001),
                leading_edge_genes_json=p.get("leading_edge_genes_json", []),
            )
            self._session.add(pathway)
            created.append(pathway)

        await self._session.flush()
        return created

    async def get_dataset_coordinates(
        self,
        dataset_id: uuid.UUID | str,
        limit: int = 2000,
    ) -> List[DBCellCoordinate]:
        """Fetch 2D cell coordinates for scatter plot visualization."""
        stmt = (
            select(DBCellCoordinate)
            .where(DBCellCoordinate.dataset_id == dataset_id)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_dataset_markers(
        self,
        dataset_id: uuid.UUID | str,
        cluster_index: Optional[int] = None,
    ) -> List[DBDifferentialGene]:
        """Fetch differential expression marker genes."""
        stmt = select(DBDifferentialGene).where(DBDifferentialGene.dataset_id == dataset_id)
        if cluster_index is not None:
            stmt = stmt.where(DBDifferentialGene.cluster_index == cluster_index)
        stmt = stmt.order_by(desc(DBDifferentialGene.log2_fold_change))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete_dataset(self, dataset_id: uuid.UUID | str) -> bool:
        """Delete single-cell dataset and cascaded records."""
        stmt = select(DBSingleCellDataset).where(DBSingleCellDataset.id == dataset_id)
        result = await self._session.execute(stmt)
        ds = result.scalar_one_or_none()
        if not ds:
            return False
        await self._session.delete(ds)
        await self._session.flush()
        return True
