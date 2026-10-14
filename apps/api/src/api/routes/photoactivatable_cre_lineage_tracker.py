"""FastAPI routes for Phase 479: Autonomous Optogenetic Photoactivatable Cre-Lox Recombinase Genomic Barcode Lineage Tracker."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.photoactivatable_cre_lineage_tracker_repo import PhotoactivatableCreLineageTrackerRepository
from research.orchestration.photoactivatable_cre_lineage_tracker_engine import PhotoactivatableCreLineageTrackerEngine

router = APIRouter(prefix="/photoactivatable-cre-lineage-tracker", tags=["photoactivatable-cre-lineage-tracker"])


class AnalyzePhotoactivatableCreLineageTrackerRequest(BaseModel):
    name: str = Field(..., example="Autonomous Optogenetic Photoactivatable Cre-Lox Recombinase Genomic Barcode Lineage Tracker Run")
    target_specimen: str = Field(default="Split Magnet-Cre Recombinase Knock-In Neural Crest Stem Cell Line with LoxP Barcode Cassette")
    analytical_modality: str = Field(default="photoactivatable-cre-lineage-tracking")
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


class PhotoactivatableCreLineageTrackerStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    photoinduction_recombination_efficiency: float
    dark_state_leakage_recombination_rate: float
    spatial_focal_lineage_resolution_um: float
    clonal_barcode_diversity_entropy: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=PhotoactivatableCreLineageTrackerStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_photoactivatable_cre_lineage_tracker(
    req: AnalyzePhotoactivatableCreLineageTrackerRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Optogenetic Photoactivatable Cre-Lox Recombinase Genomic Barcode Lineage Tracker analysis and persist study."""
    engine = PhotoactivatableCreLineageTrackerEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = PhotoactivatableCreLineageTrackerRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        photoinduction_recombination_efficiency=result.photoinduction_recombination_efficiency,
        dark_state_leakage_recombination_rate=result.dark_state_leakage_recombination_rate,
        spatial_focal_lineage_resolution_um=result.spatial_focal_lineage_resolution_um,
        clonal_barcode_diversity_entropy=result.clonal_barcode_diversity_entropy,
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

    return PhotoactivatableCreLineageTrackerStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        photoinduction_recombination_efficiency=study.photoinduction_recombination_efficiency,
        dark_state_leakage_recombination_rate=study.dark_state_leakage_recombination_rate,
        spatial_focal_lineage_resolution_um=study.spatial_focal_lineage_resolution_um,
        clonal_barcode_diversity_entropy=study.clonal_barcode_diversity_entropy,
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


@router.get("/studies", response_model=List[PhotoactivatableCreLineageTrackerStudyResponse])
async def list_photoactivatable_cre_lineage_tracker_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Optogenetic Photoactivatable Cre-Lox Recombinase Genomic Barcode Lineage Tracker studies."""
    repo = PhotoactivatableCreLineageTrackerRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=PhotoactivatableCreLineageTrackerStudyResponse)
async def get_photoactivatable_cre_lineage_tracker_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Optogenetic Photoactivatable Cre-Lox Recombinase Genomic Barcode Lineage Tracker study by ID."""
    repo = PhotoactivatableCreLineageTrackerRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
