"""FastAPI route for Phase 571: Autonomous High-Plex Microfluidic Spatial In-Situ CUT&Tag Chromatin Modification Niche Profiler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.single_cell_spatial_epigenomic_cut_and_tag_repo import SingleCellSpatialEpigenomicCutAndTagRepository
from research.orchestration.single_cell_spatial_epigenomic_cut_and_tag_engine import SingleCellSpatialEpigenomicCutAndTagEngine

router = APIRouter(prefix="/single-cell-spatial-epigenomic-cut-and-tag", tags=["Phase 571 - Autonomous High-Plex Microfluidic Spatial In-Situ CUT&Tag Chromatin Modification Niche Profiler"])


class SingleCellSpatialEpigenomicCutAndTagAnalyzeRequest(BaseModel):
    name: str = Field(default="Autonomous High-Plex Microfluidic Spatial In-Situ CUT&Tag Chromatin Modification Niche Profiler Study")
    target_specimen: Optional[str] = Field(default="Murine Embryonic Cortex Cryosection Microfluidic Deterministic Barcoding CUT&Tag for H3K27me3 and H3K4me3")
    analytical_modality: Optional[str] = Field(default="spatial-cut-and-tag-epigenomics")
    input_scale: float = Field(default=1.0, ge=0.1, le=10.0)


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


class SingleCellSpatialEpigenomicCutAndTagStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    chromatin_enrichment_specificity: float
    spatial_barcoding_purity: float
    signal_to_background_promoter_ratio: float
    niche_clustering_silhouette: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []


@router.post("/analyze", response_model=SingleCellSpatialEpigenomicCutAndTagStudyResponse)
async def analyze_single_cell_spatial_epigenomic_cut_and_tag(
    req: SingleCellSpatialEpigenomicCutAndTagAnalyzeRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Execute autonomous analysis for Autonomous High-Plex Microfluidic Spatial In-Situ CUT&Tag Chromatin Modification Niche Profiler."""
    engine = SingleCellSpatialEpigenomicCutAndTagEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SingleCellSpatialEpigenomicCutAndTagRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        chromatin_enrichment_specificity=result.chromatin_enrichment_specificity,
        spatial_barcoding_purity=result.spatial_barcoding_purity,
        signal_to_background_promoter_ratio=result.signal_to_background_promoter_ratio,
        niche_clustering_silhouette=result.niche_clustering_silhouette,
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

    return SingleCellSpatialEpigenomicCutAndTagStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        chromatin_enrichment_specificity=study.chromatin_enrichment_specificity,
        spatial_barcoding_purity=study.spatial_barcoding_purity,
        signal_to_background_promoter_ratio=study.signal_to_background_promoter_ratio,
        niche_clustering_silhouette=study.niche_clustering_silhouette,
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


@router.get("/studies", response_model=List[SingleCellSpatialEpigenomicCutAndTagStudyResponse])
async def list_single_cell_spatial_epigenomic_cut_and_tag_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous High-Plex Microfluidic Spatial In-Situ CUT&Tag Chromatin Modification Niche Profiler studies."""
    repo = SingleCellSpatialEpigenomicCutAndTagRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SingleCellSpatialEpigenomicCutAndTagStudyResponse)
async def get_single_cell_spatial_epigenomic_cut_and_tag_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous High-Plex Microfluidic Spatial In-Situ CUT&Tag Chromatin Modification Niche Profiler study by ID."""
    repo = SingleCellSpatialEpigenomicCutAndTagRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
