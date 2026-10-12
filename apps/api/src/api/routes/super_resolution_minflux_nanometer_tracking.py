"""FastAPI routes for Phase 440: Autonomous Interferometric MINFLUX Nanometer Single-Fluorophore Dynamic Tracking Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.super_resolution_minflux_nanometer_tracking_repo import MinfluxNanometerTrackingRepository
from research.orchestration.super_resolution_minflux_nanometer_tracking_engine import MinfluxNanometerTrackingEngine

router = APIRouter(prefix="/minflux-nanometer-tracking", tags=["minflux-nanometer-tracking"])


class AnalyzeMinfluxNanometerTrackingRequest(BaseModel):
    name: str = Field(..., example="Autonomous Interferometric MINFLUX Nanometer Single-Fluorophore Dynamic Tracking Engine Run")
    target_specimen: str = Field(default="Living Motor Protein Myosin V Moving Along Actin Filament with Cy5 Label")
    analytical_modality: str = Field(default="minflux-tracking")
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


class MinfluxNanometerTrackingStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    spatial_localization_precision_angstrom: float
    temporal_resolution_us: float
    photon_budget_efficiency_ratio: float
    step_size_hand_over_hand_nm: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=MinfluxNanometerTrackingStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_super_resolution_minflux_nanometer_tracking(
    req: AnalyzeMinfluxNanometerTrackingRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Interferometric MINFLUX Nanometer Single-Fluorophore Dynamic Tracking Engine analysis and persist study."""
    engine = MinfluxNanometerTrackingEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = MinfluxNanometerTrackingRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        spatial_localization_precision_angstrom=result.spatial_localization_precision_angstrom,
        temporal_resolution_us=result.temporal_resolution_us,
        photon_budget_efficiency_ratio=result.photon_budget_efficiency_ratio,
        step_size_hand_over_hand_nm=result.step_size_hand_over_hand_nm,
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

    return MinfluxNanometerTrackingStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        spatial_localization_precision_angstrom=study.spatial_localization_precision_angstrom,
        temporal_resolution_us=study.temporal_resolution_us,
        photon_budget_efficiency_ratio=study.photon_budget_efficiency_ratio,
        step_size_hand_over_hand_nm=study.step_size_hand_over_hand_nm,
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


@router.get("/studies", response_model=List[MinfluxNanometerTrackingStudyResponse])
async def list_super_resolution_minflux_nanometer_tracking_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Interferometric MINFLUX Nanometer Single-Fluorophore Dynamic Tracking Engine studies."""
    repo = MinfluxNanometerTrackingRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=MinfluxNanometerTrackingStudyResponse)
async def get_super_resolution_minflux_nanometer_tracking_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Interferometric MINFLUX Nanometer Single-Fluorophore Dynamic Tracking Engine study by ID."""
    repo = MinfluxNanometerTrackingRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
