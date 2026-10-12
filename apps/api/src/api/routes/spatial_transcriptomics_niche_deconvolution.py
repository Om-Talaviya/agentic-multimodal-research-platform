"""FastAPI routes for Phase 431: Autonomous High-Plex Spatial Transcriptomics Spot Deconvolution & Cell-Type Niche Interaction Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.spatial_transcriptomics_niche_deconvolution_repo import SpatialTranscriptomicsNicheDeconvolutionRepository
from research.orchestration.spatial_transcriptomics_niche_deconvolution_engine import SpatialTranscriptomicsNicheDeconvolutionEngine

router = APIRouter(prefix="/spatial-transcriptomics-niche-deconvolution", tags=["spatial-transcriptomics-niche-deconvolution"])


class AnalyzeSpatialTranscriptomicsNicheDeconvolutionRequest(BaseModel):
    name: str = Field(..., example="Autonomous High-Plex Spatial Transcriptomics Spot Deconvolution & Cell-Type Niche Interaction Engine Run")
    target_specimen: str = Field(default="10x Visium HD Formalin-Fixed Paraffin-Embedded Tissue Slice")
    analytical_modality: str = Field(default="spatial-niche-deconvolution")
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


class SpatialTranscriptomicsNicheDeconvolutionStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    sub_spot_cell_type_purity: float
    niche_cross_talk_significance_p: float
    ligand_receptor_spatial_correlation: float
    microenvironment_entropy_index: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=SpatialTranscriptomicsNicheDeconvolutionStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_spatial_transcriptomics_niche_deconvolution(
    req: AnalyzeSpatialTranscriptomicsNicheDeconvolutionRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous High-Plex Spatial Transcriptomics Spot Deconvolution & Cell-Type Niche Interaction Engine analysis and persist study."""
    engine = SpatialTranscriptomicsNicheDeconvolutionEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SpatialTranscriptomicsNicheDeconvolutionRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        sub_spot_cell_type_purity=result.sub_spot_cell_type_purity,
        niche_cross_talk_significance_p=result.niche_cross_talk_significance_p,
        ligand_receptor_spatial_correlation=result.ligand_receptor_spatial_correlation,
        microenvironment_entropy_index=result.microenvironment_entropy_index,
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

    return SpatialTranscriptomicsNicheDeconvolutionStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        sub_spot_cell_type_purity=study.sub_spot_cell_type_purity,
        niche_cross_talk_significance_p=study.niche_cross_talk_significance_p,
        ligand_receptor_spatial_correlation=study.ligand_receptor_spatial_correlation,
        microenvironment_entropy_index=study.microenvironment_entropy_index,
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


@router.get("/studies", response_model=List[SpatialTranscriptomicsNicheDeconvolutionStudyResponse])
async def list_spatial_transcriptomics_niche_deconvolution_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous High-Plex Spatial Transcriptomics Spot Deconvolution & Cell-Type Niche Interaction Engine studies."""
    repo = SpatialTranscriptomicsNicheDeconvolutionRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SpatialTranscriptomicsNicheDeconvolutionStudyResponse)
async def get_spatial_transcriptomics_niche_deconvolution_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous High-Plex Spatial Transcriptomics Spot Deconvolution & Cell-Type Niche Interaction Engine study by ID."""
    repo = SpatialTranscriptomicsNicheDeconvolutionRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
