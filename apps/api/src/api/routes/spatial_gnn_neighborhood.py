"""
Phase 139: Spatial Multi-Omics Cell-Cell GNN Neighborhood Co-Occurrence Matrix API Route.
"""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.spatial_gnn_neighborhood_repo import (
    SpatialGNNNeighborhoodRepository,
)
from research.spatial.spatial_gnn_engine import (
    SpatialGNNNeighborhoodEngine,
)

router = APIRouter(prefix="/spatial-gnn", tags=["Spatial Multi-Omics GNN Neighborhoods"])


class SpatialGNNMatrixRequest(BaseModel):
    dataset_name: str = Field(..., example="CosMx_NSCLC_Immune_Atlas")
    tissue_type: str = Field(..., example="Non-Small Cell Lung Carcinoma")
    radius_um: float = Field(default=50.0, example=50.0)
    embedding_dim: int = Field(default=128, example=128)
    cell_types: Optional[List[str]] = None
    workspace_id: Optional[str] = None


@router.post("/build-matrix", status_code=status.HTTP_201_CREATED)
async def build_spatial_gnn_matrix_endpoint(
    req: SpatialGNNMatrixRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = SpatialGNNNeighborhoodEngine()
    result = engine.build_spatial_neighborhood_matrix(
        dataset_name=req.dataset_name,
        tissue_type=req.tissue_type,
        radius_um=req.radius_um,
        embedding_dim=req.embedding_dim,
        cell_types=req.cell_types,
    )

    repo = SpatialGNNNeighborhoodRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else None

    nb = await repo.create_neighborhood(
        project_id=ws_id,
        dataset_name=result.dataset_name,
        tissue_type=result.tissue_type,
        total_single_cells_indexed=result.total_cells,
        graph_connectivity_radius_um=req.radius_um,
        gnn_embedding_dimension=req.embedding_dim,
        spatial_homophily_ratio=result.spatial_homophily_ratio,
        metadata_json={
            "ligand_receptor_networks": result.ligand_receptor_networks,
            "recommendations": result.recommendations,
        },
    )

    # Add proximity graphs
    for edge in result.co_occurrence_edges:
        await repo.add_proximity_graph(
            neighborhood_id=nb.id,
            source_cell_type=edge["source"],
            target_cell_type=edge["target"],
            interaction_frequency=edge["interaction_count"],
            spatial_enrichment_z_score=edge["z_score"],
            ligand_receptor_potential_score=0.85,
        )

    # Add microdomain niches
    for niche in result.spatial_niches:
        await repo.add_microdomain_niche(
            neighborhood_id=nb.id,
            niche_cluster_id=niche["niche_id"],
            dominant_cell_composition=niche["composition"],
            mean_distance_to_vasculature_um=niche["mean_distance_vasculature_um"],
            hypoxia_signature_enrichment=niche["hypoxia_signature"],
        )

    return {
        "status": "SUCCESS",
        "neighborhood_id": str(nb.id),
        "dataset_name": nb.dataset_name,
        "total_cells": nb.total_single_cells_indexed,
        "spatial_homophily_ratio": nb.spatial_homophily_ratio,
        "result": result.model_dump(),
    }


@router.get("/neighborhoods/{neighborhood_id}")
async def get_spatial_gnn_neighborhood(
    neighborhood_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        nid = uuid.UUID(neighborhood_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid neighborhood UUID")

    repo = SpatialGNNNeighborhoodRepository(db)
    nb = await repo.get_neighborhood(nid)
    if not nb:
        raise HTTPException(status_code=404, detail="Spatial GNN neighborhood not found")

    return {
        "id": str(nb.id),
        "dataset_name": nb.dataset_name,
        "tissue_type": nb.tissue_type,
        "proximity_graphs_count": len(nb.proximity_graphs),
        "microdomain_niches_count": len(nb.microdomain_niches),
    }
