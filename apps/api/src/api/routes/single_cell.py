"""Autonomous Multi-Omics & Single-Cell Transcriptomics API Routes (Phase 41)."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db_session
from database.models.user import User as DBUser
from database.repositories.single_cell_repo import SingleCellRepository
from research.single_cell_engine import SingleCellTranscriptomicsEngine
from shared.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/single-cell", tags=["single-cell"])
engine = SingleCellTranscriptomicsEngine()


# --- Pydantic Request / Response Schemas ---

class SingleCellAnalyzeRequest(BaseModel):
    dataset_title: str = Field(..., description="Dataset title (e.g. Human Liver scRNA-seq LNP Uptake Atlas)")
    organism: str = Field("Homo sapiens", description="Host organism (e.g. Homo sapiens, Mus musculus)")
    tissue: str = Field("Liver", description="Target tissue (e.g. Liver, PBMC, Brain, Tumor)")
    sequencing_platform: str = Field("10x Chromium Next GEM 3' v3.1", description="Sequencing platform chemistry")
    clustering_resolution: float = Field(0.5, ge=0.1, le=2.0, description="Graph clustering resolution parameter")
    total_cells: int = Field(600, ge=50, le=2500, description="Total single cells to simulate/analyze")
    workspace_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None


# --- Endpoint Implementations ---

@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_single_cell_dataset(
    payload: SingleCellAnalyzeRequest,
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Execute complete single-cell transcriptomics analysis, graph clustering, UMAP embedding, differential expression, and GSEA."""
    result = engine.analyze_single_cell_dataset(
        dataset_title=payload.dataset_title,
        organism=payload.organism,
        tissue=payload.tissue,
        sequencing_platform=payload.sequencing_platform,
        clustering_resolution=payload.clustering_resolution,
        total_cells_to_simulate=payload.total_cells,
    )

    repo = SingleCellRepository(session)
    dataset = await repo.create_dataset(
        user_id=current_user.id,
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
        dataset_title=result.dataset_title,
        organism=result.organism,
        tissue=result.tissue,
        sequencing_platform=result.sequencing_platform,
        total_cells=result.total_cells,
        total_genes=result.total_genes,
        clustering_resolution=result.clustering_resolution,
        metadata_json=result.metadata_json,
    )

    # Persist Clusters
    clusters_data = [c.model_dump() for c in result.clusters]
    created_clusters = await repo.add_clusters(dataset.id, clusters_data)

    # Persist Coordinates
    coords_data = [coord.model_dump() for coord in result.cell_coordinates]
    await repo.add_cell_coordinates(dataset.id, coords_data)

    # Persist Differential Genes
    diff_data = [dg.model_dump() for dg in result.differential_genes]
    await repo.add_differential_genes(dataset.id, diff_data)

    # Persist Pathway Enrichments
    path_data = [p.model_dump() for p in result.pathway_enrichments]
    await repo.add_pathway_enrichments(dataset.id, path_data)

    return {
        "dataset_id": str(dataset.id),
        "dataset_title": dataset.dataset_title,
        "organism": dataset.organism,
        "tissue": dataset.tissue,
        "total_cells": dataset.total_cells,
        "total_genes": dataset.total_genes,
        "clusters_count": len(created_clusters),
        "clusters": [
            {
                "id": str(c.id),
                "cluster_index": c.cluster_index,
                "cell_type_annotation": c.cell_type_annotation,
                "cell_count": c.cell_count,
                "percentage_of_total": c.percentage_of_total,
                "top_markers": c.top_markers_json,
            }
            for c in created_clusters
        ],
        "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
    }


@router.get("/datasets", status_code=status.HTTP_200_OK)
async def list_single_cell_datasets(
    workspace_id: Optional[uuid.UUID] = Query(None),
    project_id: Optional[uuid.UUID] = Query(None),
    tissue: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """List single-cell datasets for the current user."""
    repo = SingleCellRepository(session)
    datasets = await repo.list_datasets(
        user_id=current_user.id,
        workspace_id=workspace_id,
        project_id=project_id,
        tissue=tissue,
        limit=limit,
        offset=offset,
    )

    items = []
    for d in datasets:
        items.append({
            "id": str(d.id),
            "user_id": str(d.user_id),
            "workspace_id": str(d.workspace_id) if d.workspace_id else None,
            "project_id": str(d.project_id) if d.project_id else None,
            "dataset_title": d.dataset_title,
            "organism": d.organism,
            "tissue": d.tissue,
            "sequencing_platform": d.sequencing_platform,
            "total_cells": d.total_cells,
            "total_genes": d.total_genes,
            "clustering_resolution": d.clustering_resolution,
            "clusters_count": len(d.clusters) if d.clusters else 0,
            "metadata_json": d.metadata_json,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        })

    return {
        "items": items,
        "count": len(items),
        "limit": limit,
        "offset": offset,
    }


@router.get("/datasets/{dataset_id}", status_code=status.HTTP_200_OK)
async def get_single_cell_dataset(
    dataset_id: uuid.UUID,
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Retrieve full single-cell dataset details including clusters, marker genes, and GSEA pathways."""
    repo = SingleCellRepository(session)
    d = await repo.get_dataset(dataset_id)
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Single-cell dataset not found")

    return {
        "id": str(d.id),
        "user_id": str(d.user_id),
        "workspace_id": str(d.workspace_id) if d.workspace_id else None,
        "project_id": str(d.project_id) if d.project_id else None,
        "dataset_title": d.dataset_title,
        "organism": d.organism,
        "tissue": d.tissue,
        "sequencing_platform": d.sequencing_platform,
        "total_cells": d.total_cells,
        "total_genes": d.total_genes,
        "clustering_resolution": d.clustering_resolution,
        "metadata_json": d.metadata_json,
        "clusters": [
            {
                "id": str(c.id),
                "cluster_index": c.cluster_index,
                "cell_type_annotation": c.cell_type_annotation,
                "cell_count": c.cell_count,
                "percentage_of_total": c.percentage_of_total,
                "top_markers": c.top_markers_json,
            }
            for c in d.clusters
        ],
        "differential_genes": [
            {
                "id": str(g.id),
                "cluster_index": g.cluster_index,
                "gene_symbol": g.gene_symbol,
                "log2_fold_change": g.log2_fold_change,
                "p_value": g.p_value,
                "p_val_adj": g.p_val_adj,
                "pct_in_cluster": g.pct_in_cluster,
                "pct_out_of_cluster": g.pct_out_of_cluster,
                "is_significant": g.is_significant,
            }
            for g in d.differential_genes
        ],
        "pathway_enrichments": [
            {
                "id": str(p.id),
                "cluster_index": p.cluster_index,
                "pathway_name": p.pathway_name,
                "database_source": p.database_source,
                "normalized_enrichment_score": p.normalized_enrichment_score,
                "p_val_adj": p.p_val_adj,
                "leading_edge_genes": p.leading_edge_genes_json,
            }
            for p in d.pathway_enrichments
        ],
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }


@router.get("/datasets/{dataset_id}/coordinates", status_code=status.HTTP_200_OK)
async def get_dataset_coordinates(
    dataset_id: uuid.UUID,
    limit: int = Query(2000, ge=10, le=5000),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Fetch 2D UMAP and t-SNE cell coordinates for scatter plot visualization."""
    repo = SingleCellRepository(session)
    coords = await repo.get_dataset_coordinates(dataset_id, limit=limit)
    return {
        "dataset_id": str(dataset_id),
        "total_coordinates": len(coords),
        "coordinates": [
            {
                "cell_barcode": c.cell_barcode,
                "cluster_index": c.cluster_index,
                "umap_x": c.umap_x,
                "umap_y": c.umap_y,
                "tsne_x": c.tsne_x,
                "tsne_y": c.tsne_y,
                "pseudotime": c.pseudotime_value,
                "cell_type": c.cell_type_annotation,
            }
            for c in coords
        ],
    }


@router.get("/datasets/{dataset_id}/markers", status_code=status.HTTP_200_OK)
async def get_dataset_markers(
    dataset_id: uuid.UUID,
    cluster_index: Optional[int] = Query(None),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Fetch differential expression marker genes with volcano plot data."""
    repo = SingleCellRepository(session)
    markers = await repo.get_dataset_markers(dataset_id, cluster_index=cluster_index)
    return {
        "dataset_id": str(dataset_id),
        "cluster_index": cluster_index,
        "count": len(markers),
        "markers": [
            {
                "id": str(m.id),
                "cluster_index": m.cluster_index,
                "gene_symbol": m.gene_symbol,
                "log2_fold_change": m.log2_fold_change,
                "p_value": m.p_value,
                "p_val_adj": m.p_val_adj,
                "pct_in_cluster": m.pct_in_cluster,
                "pct_out_of_cluster": m.pct_out_of_cluster,
                "is_significant": m.is_significant,
            }
            for m in markers
        ],
    }


@router.delete("/datasets/{dataset_id}", status_code=status.HTTP_200_OK)
async def delete_single_cell_dataset(
    dataset_id: uuid.UUID,
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Delete a single-cell dataset and cascaded records."""
    repo = SingleCellRepository(session)
    success = await repo.delete_dataset(dataset_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Single-cell dataset not found")
    return {"status": "deleted", "dataset_id": str(dataset_id)}
