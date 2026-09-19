"""API Routes for Spatial Transcriptomics & TME Cellular Deconvolution."""

import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.spatial_transcriptomics_repo import SpatialTranscriptomicsRepository
from research.spatial.transcriptomics_engine import SpatialTranscriptomicsEngine

router = APIRouter(prefix="/spatial-transcriptomics", tags=["Spatial Transcriptomics & TME"])


class SpatialDeconvolutionRequest(BaseModel):
    sample_name: str = Field(..., example="Breast_Carcinoma_Section_A1")
    tissue_type: str = Field(..., example="HER2+ Invasive Ductal Carcinoma")
    platform: str = Field(default="10x Visium HD", example="10x Visium HD")
    total_spots: int = Field(default=4992, example=4992)
    workspace_id: Optional[str] = None


@router.get("/signatures")
async def get_reference_cell_signatures():
    """Retrieve canonical single-cell reference marker signatures."""
    return {"signatures": SpatialTranscriptomicsEngine.REFERENCE_SIGNATURES}


@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def analyze_spatial_slice(
    request: SpatialDeconvolutionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Run spatial deconvolution, classify TME niches, and store slice profile."""
    engine = SpatialTranscriptomicsEngine()
    result = engine.deconvolve_and_analyze(
        sample_name=request.sample_name,
        tissue_type=request.tissue_type,
        platform=request.platform,
        total_spots=request.total_spots,
    )

    repo = SpatialTranscriptomicsRepository(db)
    ws_id = uuid.UUID(request.workspace_id) if request.workspace_id else uuid.uuid4()

    slice_obj = await repo.create_slice(
        workspace_id=ws_id,
        sample_name=result["sample_name"],
        tissue_type=result["tissue_type"],
        platform=result["platform"],
        total_spots=result["total_spots"],
        median_genes_per_spot=result["median_genes_per_spot"],
        deconvolution_algorithm=result["deconvolution_algorithm"],
        spatial_entropy_score=result["spatial_entropy_score"],
        analysis_metadata={
            "immunophenotype": result["immunophenotype"],
            "tme_summary": result["tme_summary"],
        },
    )

    for cp in result["cell_proportions"]:
        await repo.add_cell_proportion(
            slice_id=slice_obj.id,
            cell_type=cp["cell_type"],
            mean_abundance_fraction=cp["mean_abundance_fraction"],
            spatial_enrichment_zone=cp["spatial_enrichment_zone"],
            marker_genes=cp["marker_genes"],
        )

    for lr in result["ligand_receptor_networks"]:
        await repo.add_ligand_receptor(
            slice_id=slice_obj.id,
            ligand_gene=lr["ligand_gene"],
            receptor_gene=lr["receptor_gene"],
            sender_cell_type=lr["sender_cell_type"],
            receiver_cell_type=lr["receiver_cell_type"],
            communication_score=lr["communication_score"],
            p_value=lr["p_value"],
            spatial_colocalization_score=lr["spatial_colocalization_score"],
        )

    return {
        "status": "SUCCESS",
        "slice_id": str(slice_obj.id),
        "sample_name": slice_obj.sample_name,
        "tissue_type": slice_obj.tissue_type,
        "spatial_entropy_score": slice_obj.spatial_entropy_score,
        "immunophenotype": result["immunophenotype"],
        "cell_proportions": result["cell_proportions"],
        "ligand_receptor_networks": result["ligand_receptor_networks"],
        "tme_summary": result["tme_summary"],
    }


@router.get("/slice/{slice_id}")
async def get_slice_details(
    slice_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Retrieve full spatial transcriptomics slice data by ID."""
    repo = SpatialTranscriptomicsRepository(db)
    try:
        sid = uuid.UUID(slice_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid slice UUID format")

    slice_obj = await repo.get_slice(sid)
    if not slice_obj:
        raise HTTPException(status_code=404, detail="Spatial slice not found")

    return {
        "id": str(slice_obj.id),
        "sample_name": slice_obj.sample_name,
        "tissue_type": slice_obj.tissue_type,
        "platform": slice_obj.platform,
        "total_spots": slice_obj.total_spots,
        "spatial_entropy_score": slice_obj.spatial_entropy_score,
        "analysis_metadata": slice_obj.analysis_metadata,
        "cell_proportions": [
            {
                "cell_type": cp.cell_type,
                "mean_abundance_fraction": cp.mean_abundance_fraction,
                "spatial_enrichment_zone": cp.spatial_enrichment_zone,
            }
            for cp in slice_obj.cell_proportions
        ],
        "ligand_receptors": [
            {
                "ligand_gene": lr.ligand_gene,
                "receptor_gene": lr.receptor_gene,
                "sender": lr.sender_cell_type,
                "receiver": lr.receiver_cell_type,
                "score": lr.communication_score,
            }
            for lr in slice_obj.ligand_receptors
        ],
    }
