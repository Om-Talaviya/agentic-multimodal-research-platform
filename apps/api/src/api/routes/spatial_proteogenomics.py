"""API Router for Spatial Proteogenomics & Subcellular Protein-RNA Co-Localization."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db
from database.repositories.spatial_proteogenomics_repo import SpatialProteogenomicsRepository
from research.spatial.spatial_proteogenomics_engine import SpatialProteogenomicsEngine

router = APIRouter(prefix="/spatial-proteogenomics", tags=["Spatial Proteogenomics"])


class SpatialSpotInput(BaseModel):
    spot_barcode: str = Field("SPOT_A1_001", description="Spatial barcode identifier")
    x_coord: float = Field(124.5, description="Spatial X coordinate in microns")
    y_coord: float = Field(450.2, description="Spatial Y coordinate in microns")
    target_mrna_symbol: str = Field("EGFR", description="Target mRNA transcript symbol")
    mrna_normalized_count: float = Field(48.2, description="Normalized transcript count")
    target_protein_antibody: str = Field("Total-EGFR (Clone D38B1)", description="Target antibody clone")
    protein_adt_signal: float = Field(1420.0, description="ADT antibody derived tag count")
    colocalization_pearson_r: float = Field(0.91, description="Protein-RNA co-localization Pearson correlation")
    subcellular_niche: str = Field("Invasive Glioblastoma Core", description="Subcellular tissue niche category")


class RunSpatialProteogenomicsRequest(BaseModel):
    study_name: str = Field(..., description="Name for the spatial proteogenomics study")
    tissue_sample_id: str = Field("GBM_TME_Slice_04", description="Tissue slice sample identifier")
    custom_spots: Optional[List[SpatialSpotInput]] = None


@router.post("/analyze", status_code=status.HTTP_201_CREATED)
async def run_spatial_proteogenomic_analysis(
    payload: RunSpatialProteogenomicsRequest,
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Execute spatial proteogenomic co-localization analysis and niche quantification."""
    engine = SpatialProteogenomicsEngine()
    spots_data = [s.model_dump() for s in payload.custom_spots] if payload.custom_spots else None

    result = engine.run_spatial_proteogenomic_analysis(
        study_name=payload.study_name,
        tissue_sample_id=payload.tissue_sample_id,
        custom_spots=spots_data,
    )

    repo = SpatialProteogenomicsRepository(session)
    saved_study = await repo.create_study(
        study_name=result["study_name"],
        tissue_sample_id=result["tissue_sample_id"],
        total_spots_analyzed=result["total_spots_analyzed"],
        mean_pearson_colocalization_r=result["mean_pearson_colocalization_r"],
        subcellular_niche_count=result["subcellular_niche_count"],
        summary_metrics=result["summary_metrics"],
        spots=result["spots"],
        enrichment_metrics=result["enrichment_metrics"],
    )

    return {
        "id": str(saved_study.id),
        "status": "success",
        "study_name": saved_study.study_name,
        "tissue_sample_id": saved_study.tissue_sample_id,
        "total_spots_analyzed": saved_study.total_spots_analyzed,
        "mean_pearson_colocalization_r": saved_study.mean_pearson_colocalization_r,
        "subcellular_niche_count": saved_study.subcellular_niche_count,
        "summary_metrics": saved_study.summary_metrics,
        "spots": [
            {
                "id": str(s.id),
                "spot_barcode": s.spot_barcode,
                "x_coord": s.x_coord,
                "y_coord": s.y_coord,
                "target_mrna_symbol": s.target_mrna_symbol,
                "mrna_normalized_count": s.mrna_normalized_count,
                "target_protein_antibody": s.target_protein_antibody,
                "protein_adt_signal": s.protein_adt_signal,
                "colocalization_pearson_r": s.colocalization_pearson_r,
                "subcellular_niche": s.subcellular_niche,
            }
            for s in saved_study.spots
        ],
        "enrichment_metrics": [
            {
                "id": str(e.id),
                "marker_pair": e.marker_pair,
                "enrichment_z_score": e.enrichment_z_score,
                "fdr_q_value": e.fdr_q_value,
                "biological_relevance": e.biological_relevance,
            }
            for e in saved_study.enrichment_metrics
        ],
    }


@router.get("/studies", response_model=List[Dict[str, Any]])
async def list_spatial_proteogenomic_studies(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """List recent spatial proteogenomics studies."""
    repo = SpatialProteogenomicsRepository(session)
    studies = await repo.list_studies(limit=limit, offset=offset)
    return [
        {
            "id": str(s.id),
            "study_name": s.study_name,
            "tissue_sample_id": s.tissue_sample_id,
            "total_spots_analyzed": s.total_spots_analyzed,
            "mean_pearson_colocalization_r": s.mean_pearson_colocalization_r,
            "subcellular_niche_count": s.subcellular_niche_count,
            "created_at": s.created_at,
        }
        for s in studies
    ]


@router.get("/studies/{study_id}")
async def get_spatial_proteogenomic_study(
    study_id: uuid.UUID,
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve details for a specific spatial proteogenomics study."""
    repo = SpatialProteogenomicsRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spatial proteogenomics study with ID '{study_id}' not found.",
        )

    return {
        "id": str(study.id),
        "study_name": study.study_name,
        "tissue_sample_id": study.tissue_sample_id,
        "total_spots_analyzed": study.total_spots_analyzed,
        "mean_pearson_colocalization_r": study.mean_pearson_colocalization_r,
        "subcellular_niche_count": study.subcellular_niche_count,
        "summary_metrics": study.summary_metrics,
        "spots": [
            {
                "id": str(s.id),
                "spot_barcode": s.spot_barcode,
                "x_coord": s.x_coord,
                "y_coord": s.y_coord,
                "target_mrna_symbol": s.target_mrna_symbol,
                "mrna_normalized_count": s.mrna_normalized_count,
                "target_protein_antibody": s.target_protein_antibody,
                "protein_adt_signal": s.protein_adt_signal,
                "colocalization_pearson_r": s.colocalization_pearson_r,
                "subcellular_niche": s.subcellular_niche,
            }
            for s in study.spots
        ],
        "enrichment_metrics": [
            {
                "id": str(e.id),
                "marker_pair": e.marker_pair,
                "enrichment_z_score": e.enrichment_z_score,
                "fdr_q_value": e.fdr_q_value,
                "biological_relevance": e.biological_relevance,
            }
            for e in study.enrichment_metrics
        ],
        "created_at": study.created_at,
    }


@router.delete("/studies/{study_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_spatial_proteogenomic_study(
    study_id: uuid.UUID,
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    """Delete a spatial proteogenomics study record by ID."""
    repo = SpatialProteogenomicsRepository(session)
    deleted = await repo.delete_study(study_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spatial proteogenomics study with ID '{study_id}' not found.",
        )
