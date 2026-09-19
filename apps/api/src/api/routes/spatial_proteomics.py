"""API Routes for Multiplexed Spatial Proteomics & IMC Analyzer (Phase 102)."""

import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.spatial_proteomics_repo import SpatialProteomicsRepository
from research.spatial.proteomics_engine import SpatialProteomicsEngine

router = APIRouter(prefix="/spatial-proteomics", tags=["Multiplexed Spatial Proteomics"])


class SpatialProteomicsAnalysisRequest(BaseModel):
    sample_name: str = Field(..., example="Melanoma_FFPE_Tissue_IMC_01")
    tissue_origin: str = Field(..., example="Cutaneous Melanoma Stage III")
    imaging_modality: str = Field(default="Hyperion Imaging Mass Cytometry", example="Hyperion Imaging Mass Cytometry")
    segmented_cells: int = Field(default=24500, example=24500)
    workspace_id: Optional[str] = None


@router.get("/marker-panel")
async def get_marker_panel():
    """Retrieve canonical 40-channel heavy-metal conjugated antibody panel."""
    return {"markers": SpatialProteomicsEngine.PANEL_40_MARKERS}


@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_spatial_proteomics_slice(
    request: SpatialProteomicsAnalysisRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Segment, spillover-compensate, and profile cellular spatial neighborhoods from multiplexed IMC images."""
    engine = SpatialProteomicsEngine()
    result = engine.analyze_multiplex_slice(
        sample_name=request.sample_name,
        tissue_origin=request.tissue_origin,
        modality=request.imaging_modality,
        segmented_cells=request.segmented_cells,
    )

    repo = SpatialProteomicsRepository(db)
    ws_id = uuid.UUID(request.workspace_id) if request.workspace_id else uuid.uuid4()

    exp = await repo.create_experiment(
        workspace_id=ws_id,
        sample_name=result["sample_name"],
        tissue_origin=result["tissue_origin"],
        imaging_modality=result["imaging_modality"],
        total_channels=result["total_channels"],
        total_segmented_cells=result["total_segmented_cells"],
        mean_cellular_density_per_mm2=result["mean_cellular_density_per_mm2"],
        immune_infiltration_score=result["immune_infiltration_score"],
        tumor_stroma_mixing_entropy=result["tumor_stroma_mixing_entropy"],
        analysis_metadata={"summary": result["summary"]},
    )

    for ch in result["marker_channels"]:
        await repo.add_marker_channel(
            experiment_id=exp.id,
            metal_isotope_tag=ch["tag"],
            antibody_target=ch["target"],
            mean_signal_intensity=ch["intensity"],
            signal_to_noise_ratio=ch["snr"],
            positive_cells_percentage=ch["pos_pct"],
        )

    for nh in result["neighborhoods"]:
        await repo.add_neighborhood(
            experiment_id=exp.id,
            neighborhood_cluster_name=nh["neighborhood_cluster_name"],
            dominant_cell_type=nh["dominant_cell_type"],
            neighbor_cell_count=nh["neighbor_cell_count"],
            interaction_enrichment_z_score=nh["interaction_enrichment_z_score"],
        )

    return {
        "status": "SUCCESS",
        "experiment_id": str(exp.id),
        "sample_name": exp.sample_name,
        "tissue_origin": exp.tissue_origin,
        "immune_infiltration_score": exp.immune_infiltration_score,
        "tumor_stroma_mixing_entropy": exp.tumor_stroma_mixing_entropy,
        "marker_channels": result["marker_channels"],
        "neighborhoods": result["neighborhoods"],
        "summary": result["summary"],
    }


@router.get("/experiments/{experiment_id}")
async def get_spatial_proteomics_experiment(
    experiment_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Retrieve full spatial proteomics experiment details, channel intensities, and neighborhood matrices."""
    repo = SpatialProteomicsRepository(db)
    try:
        eid = uuid.UUID(experiment_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid experiment UUID format")

    exp = await repo.get_experiment(eid)
    if not exp:
        raise HTTPException(status_code=404, detail="Spatial proteomics experiment not found")

    return {
        "id": str(exp.id),
        "sample_name": exp.sample_name,
        "tissue_origin": exp.tissue_origin,
        "imaging_modality": exp.imaging_modality,
        "total_segmented_cells": exp.total_segmented_cells,
        "immune_infiltration_score": exp.immune_infiltration_score,
        "marker_channels": [
            {
                "tag": c.metal_isotope_tag,
                "target": c.antibody_target,
                "intensity": c.mean_signal_intensity,
                "pos_pct": c.positive_cells_percentage,
            }
            for c in exp.marker_channels
        ],
        "neighborhoods": [
            {
                "cluster": n.neighborhood_cluster_name,
                "cell_type": n.dominant_cell_type,
                "count": n.neighbor_cell_count,
            }
            for n in exp.neighborhoods
        ],
    }
