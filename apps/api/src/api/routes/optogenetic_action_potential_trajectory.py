"""FastAPI routes for Phase 444: Autonomous Optogenetic Membrane Depolarization & Action Potential Firing Trajectory Simulator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.optogenetic_action_potential_trajectory_repo import OptogeneticActionPotentialRepository
from research.orchestration.optogenetic_action_potential_trajectory_engine import OptogeneticActionPotentialEngine

router = APIRouter(prefix="/optogenetic-action-potential", tags=["optogenetic-action-potential"])


class AnalyzeOptogeneticActionPotentialRequest(BaseModel):
    name: str = Field(..., example="Autonomous Optogenetic Membrane Depolarization & Action Potential Firing Trajectory Simulator Run")
    target_specimen: str = Field(default="Channelrhodopsin-2 (ChR2) Expressing Cortical Pyramidal Neurons under 470nm Pulsed Blue Light")
    analytical_modality: str = Field(default="optogenetic-membrane-depolarization")
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


class OptogeneticActionPotentialStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    membrane_depolarization_rate_mv_per_ms: float
    action_potential_firing_fidelity: float
    photocurrent_amplitude_pA: float
    channel_closing_decay_tau_off_ms: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=OptogeneticActionPotentialStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_optogenetic_action_potential_trajectory(
    req: AnalyzeOptogeneticActionPotentialRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Optogenetic Membrane Depolarization & Action Potential Firing Trajectory Simulator analysis and persist study."""
    engine = OptogeneticActionPotentialEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = OptogeneticActionPotentialRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        membrane_depolarization_rate_mv_per_ms=result.membrane_depolarization_rate_mv_per_ms,
        action_potential_firing_fidelity=result.action_potential_firing_fidelity,
        photocurrent_amplitude_pA=result.photocurrent_amplitude_pA,
        channel_closing_decay_tau_off_ms=result.channel_closing_decay_tau_off_ms,
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

    return OptogeneticActionPotentialStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        membrane_depolarization_rate_mv_per_ms=study.membrane_depolarization_rate_mv_per_ms,
        action_potential_firing_fidelity=study.action_potential_firing_fidelity,
        photocurrent_amplitude_pA=study.photocurrent_amplitude_pA,
        channel_closing_decay_tau_off_ms=study.channel_closing_decay_tau_off_ms,
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


@router.get("/studies", response_model=List[OptogeneticActionPotentialStudyResponse])
async def list_optogenetic_action_potential_trajectory_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Optogenetic Membrane Depolarization & Action Potential Firing Trajectory Simulator studies."""
    repo = OptogeneticActionPotentialRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=OptogeneticActionPotentialStudyResponse)
async def get_optogenetic_action_potential_trajectory_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Optogenetic Membrane Depolarization & Action Potential Firing Trajectory Simulator study by ID."""
    repo = OptogeneticActionPotentialRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
