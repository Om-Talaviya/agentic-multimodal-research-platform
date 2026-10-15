"""FastAPI routes for Phase 528: Autonomous High-Speed Atomic Force Microscopy (HS-AFM) Myosin Motor Stepping Real-Time Profiler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.high_speed_afm_molecular_motor_dynamics_repo import HighSpeedAfmMolecularMotorDynamicsRepository
from research.orchestration.high_speed_afm_molecular_motor_dynamics_engine import HighSpeedAfmMolecularMotorDynamicsEngine

router = APIRouter(prefix="/high-speed-afm-molecular-motor-dynamics", tags=["high-speed-afm-molecular-motor-dynamics"])


class AnalyzeHighSpeedAfmMolecularMotorDynamicsRequest(BaseModel):
    name: str = Field(..., example="Autonomous High-Speed Atomic Force Microscopy (HS-AFM) Myosin Motor Stepping Real-Time Profiler Run")
    target_specimen: str = Field(default="Single Native Myosin V Dimer stepping along Immobilized Actin Filament in Microfluidic HS-AFM Cell")
    analytical_modality: str = Field(default="hs-afm-molecular-motor")
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


class HighSpeedAfmMolecularMotorDynamicsStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    hand_over_hand_step_distance_nm: float
    power_stroke_lever_arm_rotation_deg: float
    afm_cantilever_imaging_rate_fps: float
    atp_limited_dwell_time_ms: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=HighSpeedAfmMolecularMotorDynamicsStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_high_speed_afm_molecular_motor_dynamics(
    req: AnalyzeHighSpeedAfmMolecularMotorDynamicsRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous High-Speed Atomic Force Microscopy (HS-AFM) Myosin Motor Stepping Real-Time Profiler analysis and persist study."""
    engine = HighSpeedAfmMolecularMotorDynamicsEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = HighSpeedAfmMolecularMotorDynamicsRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        hand_over_hand_step_distance_nm=result.hand_over_hand_step_distance_nm,
        power_stroke_lever_arm_rotation_deg=result.power_stroke_lever_arm_rotation_deg,
        afm_cantilever_imaging_rate_fps=result.afm_cantilever_imaging_rate_fps,
        atp_limited_dwell_time_ms=result.atp_limited_dwell_time_ms,
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

    return HighSpeedAfmMolecularMotorDynamicsStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        hand_over_hand_step_distance_nm=study.hand_over_hand_step_distance_nm,
        power_stroke_lever_arm_rotation_deg=study.power_stroke_lever_arm_rotation_deg,
        afm_cantilever_imaging_rate_fps=study.afm_cantilever_imaging_rate_fps,
        atp_limited_dwell_time_ms=study.atp_limited_dwell_time_ms,
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


@router.get("/studies", response_model=List[HighSpeedAfmMolecularMotorDynamicsStudyResponse])
async def list_high_speed_afm_molecular_motor_dynamics_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous High-Speed Atomic Force Microscopy (HS-AFM) Myosin Motor Stepping Real-Time Profiler studies."""
    repo = HighSpeedAfmMolecularMotorDynamicsRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=HighSpeedAfmMolecularMotorDynamicsStudyResponse)
async def get_high_speed_afm_molecular_motor_dynamics_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous High-Speed Atomic Force Microscopy (HS-AFM) Myosin Motor Stepping Real-Time Profiler study by ID."""
    repo = HighSpeedAfmMolecularMotorDynamicsRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
