"""
FastAPI Router for Phase 162: Spatial Microdissection & Subcellular Spot Deconvolution.
"""

import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.spatial_microdissection_repo import (
    SpatialMicrodissectionRepository,
)
from research.spatial.spatial_microdissection_engine import (
    SpatialMicrodissectionEngine,
)

router = APIRouter(prefix="/spatial-microdissection", tags=["Spatial Microdissection & Subcellular Deconvolution"])


class DeconvolutionRequest(BaseModel):
    sample_name: str = Field(..., example="VisiumHD_Glioblastoma_Section4")
    tissue_type: str = Field(..., example="Glioblastoma Multiforme (GBM)")
    spot_grid_size: Optional[int] = Field(default=5, example=5)
    resolution_nm: Optional[float] = Field(default=100.0, example=100.0)
    workspace_id: Optional[str] = None


@router.post("/deconvolve", status_code=status.HTTP_201_CREATED)
async def deconvolve_spots_endpoint(
    req: DeconvolutionRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    engine = SpatialMicrodissectionEngine()
    result = engine.deconvolve_spatial_spots(
        sample_name=req.sample_name,
        tissue_type=req.tissue_type,
        spot_grid_size=req.spot_grid_size or 5,
        resolution_nm=req.resolution_nm or 100.0,
    )

    repo = SpatialMicrodissectionRepository(db)
    ws_id = uuid.UUID(req.workspace_id) if req.workspace_id else None

    session = await repo.create_session(
        sample_name=result.sample_name,
        tissue_type=result.tissue_type,
        total_spots_analyzed=result.total_spots,
        subcellular_resolution_nm=result.resolution_nm,
        deconvolution_algorithm="Subcellular-NMF-Bayesian",
        mean_cell_type_entropy=result.mean_entropy,
        project_id=ws_id,
    )

    # Save spots
    for spot in result.spots:
        await repo.add_spot_deconvolution(
            session_id=session.id,
            spot_index=spot.spot_index,
            spatial_x_coord=spot.x_coord,
            spatial_y_coord=spot.y_coord,
            dominant_cell_type=spot.dominant_cell_type,
            dominant_cell_proportion=spot.dominant_cell_proportion,
            cell_type_composition=spot.cell_type_composition,
            rna_transcripts_count=spot.rna_transcripts_count,
        )

    # Save niches
    for niche in result.niches:
        await repo.add_niche_boundary(
            session_id=session.id,
            niche_name=niche["niche_name"],
            boundary_polygon=niche["boundary_polygon"],
            niche_cellularity_score=niche["cellularity_score"],
            tumor_immune_interface_distance_um=niche["interface_distance_um"],
        )

    return {
        "status": "SUCCESS",
        "session_id": str(session.id),
        "sample_name": session.sample_name,
        "total_spots_analyzed": session.total_spots_analyzed,
        "mean_cell_type_entropy": session.mean_cell_type_entropy,
        "result": result.model_dump(),
    }


@router.get("/sessions/{session_id}")
async def get_session_endpoint(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        sid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session UUID")

    repo = SpatialMicrodissectionRepository(db)
    sess = await repo.get_session(sid)
    if not sess:
        raise HTTPException(status_code=404, detail="Spatial microdissection session not found")

    return {
        "id": str(sess.id),
        "sample_name": sess.sample_name,
        "tissue_type": sess.tissue_type,
        "total_spots_analyzed": sess.total_spots_analyzed,
        "mean_cell_type_entropy": sess.mean_cell_type_entropy,
        "deconvolutions_count": len(sess.deconvolutions),
        "niche_boundaries_count": len(sess.niche_boundaries),
    }
