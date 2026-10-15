"""FastAPI routes for Phase 532: Autonomous High-Mass-Resolution MALDI MSI Single-Cell Spatial Phospholipid Fingerprinter."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.single_cell_spatial_lipidomics_maldi_repo import SingleCellSpatialLipidomicsMaldiRepository
from research.orchestration.single_cell_spatial_lipidomics_maldi_engine import SingleCellSpatialLipidomicsMaldiEngine

router = APIRouter(prefix="/single-cell-spatial-lipidomics-maldi", tags=["single-cell-spatial-lipidomics-maldi"])


class AnalyzeSingleCellSpatialLipidomicsMaldiRequest(BaseModel):
    name: str = Field(..., example="Autonomous High-Mass-Resolution MALDI MSI Single-Cell Spatial Phospholipid Fingerprinter Run")
    target_specimen: str = Field(default="High-Precision Cryo-Sectioned Mouse Brain Cortical Layer with 5um Sub-Cellular Laser Spot")
    analytical_modality: str = Field(default="single-cell-maldi-lipidomics")
    input_scale: float = Field(default=1.0, ge=0.1, le=100.0)


class ItemProfileResponse(BaseModel):
    item_name: str
    profile_category: str
    quantitative_value: float
    log2_fold_change: float
    significance_score: float


class MetricTraceResponse(BaseModel):
    metric_dimension: str
    observed_value: float
    z_score: float
    p_value: float


class SingleCellSpatialLipidomicsMaldiStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    phospholipid_species_resolved_count: float
    spatial_laser_ablation_pitch_um: float
    mass_resolving_power_fwhm_at_m_z_800: float
    cell_type_lipidomic_silhouette_score: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=SingleCellSpatialLipidomicsMaldiStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_single_cell_spatial_lipidomics_maldi(
    req: AnalyzeSingleCellSpatialLipidomicsMaldiRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous High-Mass-Resolution MALDI MSI Single-Cell Spatial Phospholipid Fingerprinter analysis and persist study."""
    engine = SingleCellSpatialLipidomicsMaldiEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SingleCellSpatialLipidomicsMaldiRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        phospholipid_species_resolved_count=result.phospholipid_species_resolved_count,
        spatial_laser_ablation_pitch_um=result.spatial_laser_ablation_pitch_um,
        mass_resolving_power_fwhm_at_m_z_800=result.mass_resolving_power_fwhm_at_m_z_800,
        cell_type_lipidomic_silhouette_score=result.cell_type_lipidomic_silhouette_score,
        confidence_score=result.confidence_score,
        status="completed",
        summary_report=result.summary_report,
    )

    for item in result.item_profiles:
        await repo.add_item_profile(
            study_id=study.id,
            item_name=item.item_name,
            profile_category=item.profile_category,
            quantitative_value=item.quantitative_value,
            log2_fold_change=item.log2_fold_change,
            significance_score=item.significance_score,
        )

    for trace in result.metric_traces:
        await repo.add_metric_trace(
            study_id=study.id,
            metric_dimension=trace.metric_dimension,
            observed_value=trace.observed_value,
            z_score=trace.z_score,
            p_value=trace.p_value,
        )

    return SingleCellSpatialLipidomicsMaldiStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        phospholipid_species_resolved_count=study.phospholipid_species_resolved_count,
        spatial_laser_ablation_pitch_um=study.spatial_laser_ablation_pitch_um,
        mass_resolving_power_fwhm_at_m_z_800=study.mass_resolving_power_fwhm_at_m_z_800,
        cell_type_lipidomic_silhouette_score=study.cell_type_lipidomic_silhouette_score,
        confidence_score=study.confidence_score,
        status=study.status,
        summary_report=study.summary_report,
        item_profiles=[
            ItemProfileResponse(
                item_name=it.item_name,
                profile_category=it.profile_category,
                quantitative_value=it.quantitative_value,
                log2_fold_change=it.log2_fold_change,
                significance_score=it.significance_score,
            ) for it in result.item_profiles
        ],
        metric_traces=[
            MetricTraceResponse(
                metric_dimension=tr.metric_dimension,
                observed_value=tr.observed_value,
                z_score=tr.z_score,
                p_value=tr.p_value,
            ) for tr in result.metric_traces
        ],
    )


@router.get("/studies", response_model=List[SingleCellSpatialLipidomicsMaldiStudyResponse])
async def list_single_cell_spatial_lipidomics_maldi_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous High-Mass-Resolution MALDI MSI Single-Cell Spatial Phospholipid Fingerprinter studies."""
    repo = SingleCellSpatialLipidomicsMaldiRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SingleCellSpatialLipidomicsMaldiStudyResponse)
async def get_single_cell_spatial_lipidomics_maldi_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous High-Mass-Resolution MALDI MSI Single-Cell Spatial Phospholipid Fingerprinter study by ID."""
    repo = SingleCellSpatialLipidomicsMaldiRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
