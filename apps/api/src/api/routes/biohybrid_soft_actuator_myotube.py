"""FastAPI routes for Phase 457: Autonomous Biohybrid Cybernetic Soft Actuator Myotube Electromechanical Force Forecaster."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.biohybrid_soft_actuator_myotube_repo import BiohybridSoftActuatorMyotubeRepository
from research.orchestration.biohybrid_soft_actuator_myotube_engine import BiohybridSoftActuatorMyotubeEngine

router = APIRouter(prefix="/biohybrid-soft-actuator-myotube", tags=["biohybrid-soft-actuator-myotube"])


class AnalyzeBiohybridSoftActuatorMyotubeRequest(BaseModel):
    name: str = Field(..., example="Autonomous Biohybrid Cybernetic Soft Actuator Myotube Electromechanical Force Forecaster Run")
    target_specimen: str = Field(default="3D Bioprinted Optogenetic C2C12 Skeletal Myotube Cantilever on Flexible Hydrogel Skeleton")
    analytical_modality: str = Field(default="biohybrid-actuator-mechanics")
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


class BiohybridSoftActuatorMyotubeStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    active_contractile_force_micro_newtons: float
    twitch_to_tetanus_force_ratio: float
    cyclic_fatigue_endurance_cycles: float
    electromechanical_coupling_efficiency: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=BiohybridSoftActuatorMyotubeStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_biohybrid_soft_actuator_myotube(
    req: AnalyzeBiohybridSoftActuatorMyotubeRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Biohybrid Cybernetic Soft Actuator Myotube Electromechanical Force Forecaster analysis and persist study."""
    engine = BiohybridSoftActuatorMyotubeEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = BiohybridSoftActuatorMyotubeRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        active_contractile_force_micro_newtons=result.active_contractile_force_micro_newtons,
        twitch_to_tetanus_force_ratio=result.twitch_to_tetanus_force_ratio,
        cyclic_fatigue_endurance_cycles=result.cyclic_fatigue_endurance_cycles,
        electromechanical_coupling_efficiency=result.electromechanical_coupling_efficiency,
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

    return BiohybridSoftActuatorMyotubeStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        active_contractile_force_micro_newtons=study.active_contractile_force_micro_newtons,
        twitch_to_tetanus_force_ratio=study.twitch_to_tetanus_force_ratio,
        cyclic_fatigue_endurance_cycles=study.cyclic_fatigue_endurance_cycles,
        electromechanical_coupling_efficiency=study.electromechanical_coupling_efficiency,
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


@router.get("/studies", response_model=List[BiohybridSoftActuatorMyotubeStudyResponse])
async def list_biohybrid_soft_actuator_myotube_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Biohybrid Cybernetic Soft Actuator Myotube Electromechanical Force Forecaster studies."""
    repo = BiohybridSoftActuatorMyotubeRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=BiohybridSoftActuatorMyotubeStudyResponse)
async def get_biohybrid_soft_actuator_myotube_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Biohybrid Cybernetic Soft Actuator Myotube Electromechanical Force Forecaster study by ID."""
    repo = BiohybridSoftActuatorMyotubeRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
