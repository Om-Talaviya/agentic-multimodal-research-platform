"""FastAPI routes for Phase 471: Autonomous Synthetic Multicellular Somatogenesis Clock-and-Wavefront Hes7 Notch Pulse Tracker."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.somatogenesis_hes7_clock_wavefront_repo import SomatogenesisHes7ClockWavefrontRepository
from research.orchestration.somatogenesis_hes7_clock_wavefront_engine import SomatogenesisHes7ClockWavefrontEngine

router = APIRouter(prefix="/somatogenesis-hes7-clock-wavefront", tags=["somatogenesis-hes7-clock-wavefront"])


class AnalyzeSomatogenesisHes7ClockWavefrontRequest(BaseModel):
    name: str = Field(..., example="Autonomous Synthetic Multicellular Somatogenesis Clock-and-Wavefront Hes7 Notch Pulse Tracker Run")
    target_specimen: str = Field(default="Synthetic Presomitic Mesoderm (PSM) Microtissue Organoid with Oscillatory Hes7-Venus Reporter")
    analytical_modality: str = Field(default="somatogenesis-clock-wavefront")
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


class SomatogenesisHes7ClockWavefrontStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    clock_oscillation_periodicity_minutes: float
    wavefront_propagation_velocity_um_per_hr: float
    somite_boundary_sharpness_contrast_ratio: float
    synchronization_kuramoto_order_parameter: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=SomatogenesisHes7ClockWavefrontStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_somatogenesis_hes7_clock_wavefront(
    req: AnalyzeSomatogenesisHes7ClockWavefrontRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Synthetic Multicellular Somatogenesis Clock-and-Wavefront Hes7 Notch Pulse Tracker analysis and persist study."""
    engine = SomatogenesisHes7ClockWavefrontEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SomatogenesisHes7ClockWavefrontRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        clock_oscillation_periodicity_minutes=result.clock_oscillation_periodicity_minutes,
        wavefront_propagation_velocity_um_per_hr=result.wavefront_propagation_velocity_um_per_hr,
        somite_boundary_sharpness_contrast_ratio=result.somite_boundary_sharpness_contrast_ratio,
        synchronization_kuramoto_order_parameter=result.synchronization_kuramoto_order_parameter,
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

    return SomatogenesisHes7ClockWavefrontStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        clock_oscillation_periodicity_minutes=study.clock_oscillation_periodicity_minutes,
        wavefront_propagation_velocity_um_per_hr=study.wavefront_propagation_velocity_um_per_hr,
        somite_boundary_sharpness_contrast_ratio=study.somite_boundary_sharpness_contrast_ratio,
        synchronization_kuramoto_order_parameter=study.synchronization_kuramoto_order_parameter,
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


@router.get("/studies", response_model=List[SomatogenesisHes7ClockWavefrontStudyResponse])
async def list_somatogenesis_hes7_clock_wavefront_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Synthetic Multicellular Somatogenesis Clock-and-Wavefront Hes7 Notch Pulse Tracker studies."""
    repo = SomatogenesisHes7ClockWavefrontRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SomatogenesisHes7ClockWavefrontStudyResponse)
async def get_somatogenesis_hes7_clock_wavefront_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Synthetic Multicellular Somatogenesis Clock-and-Wavefront Hes7 Notch Pulse Tracker study by ID."""
    repo = SomatogenesisHes7ClockWavefrontRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
