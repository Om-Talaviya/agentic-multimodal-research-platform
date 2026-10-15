"""FastAPI routes for Phase 539: Autonomous Milestone v4.9 Planetary Cryo-Architecture, Non-Equilibrium Active Matter & Neuromorphic Quantum Bio-Computing OS Grand Meta-Orchestrator Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.milestone_v4_9_meta_orchestrator_repo import MilestoneV49MetaOrchestratorRepository
from research.orchestration.milestone_v4_9_meta_orchestrator_engine import MilestoneV49MetaOrchestratorEngine

router = APIRouter(prefix="/milestone-v4-9-meta-orchestrator", tags=["milestone-v4-9-meta-orchestrator"])


class AnalyzeMilestoneV49MetaOrchestratorRequest(BaseModel):
    name: str = Field(..., example="Autonomous Milestone v4.9 Planetary Cryo-Architecture, Non-Equilibrium Active Matter & Neuromorphic Quantum Bio-Computing OS Grand Meta-Orchestrator Engine Run")
    target_specimen: str = Field(default="Global Milestone v4.9 Distributed Multi-Agent DAG Across Phases 519-539")
    analytical_modality: str = Field(default="milestone-v4-9-planetary-orchestration")
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


class MilestoneV49MetaOrchestratorStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    cross_phase_dag_convergence_tau: float
    multi_agent_consensus_fidelity_pct: float
    sub_angstrom_simulation_accuracy_score: float
    closed_loop_autonomous_cycle_time_s: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=MilestoneV49MetaOrchestratorStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_milestone_v4_9_meta_orchestrator(
    req: AnalyzeMilestoneV49MetaOrchestratorRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Milestone v4.9 Planetary Cryo-Architecture, Non-Equilibrium Active Matter & Neuromorphic Quantum Bio-Computing OS Grand Meta-Orchestrator Engine analysis and persist study."""
    engine = MilestoneV49MetaOrchestratorEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = MilestoneV49MetaOrchestratorRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        cross_phase_dag_convergence_tau=result.cross_phase_dag_convergence_tau,
        multi_agent_consensus_fidelity_pct=result.multi_agent_consensus_fidelity_pct,
        sub_angstrom_simulation_accuracy_score=result.sub_angstrom_simulation_accuracy_score,
        closed_loop_autonomous_cycle_time_s=result.closed_loop_autonomous_cycle_time_s,
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

    return MilestoneV49MetaOrchestratorStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        cross_phase_dag_convergence_tau=study.cross_phase_dag_convergence_tau,
        multi_agent_consensus_fidelity_pct=study.multi_agent_consensus_fidelity_pct,
        sub_angstrom_simulation_accuracy_score=study.sub_angstrom_simulation_accuracy_score,
        closed_loop_autonomous_cycle_time_s=study.closed_loop_autonomous_cycle_time_s,
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


@router.get("/studies", response_model=List[MilestoneV49MetaOrchestratorStudyResponse])
async def list_milestone_v4_9_meta_orchestrator_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Milestone v4.9 Planetary Cryo-Architecture, Non-Equilibrium Active Matter & Neuromorphic Quantum Bio-Computing OS Grand Meta-Orchestrator Engine studies."""
    repo = MilestoneV49MetaOrchestratorRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=MilestoneV49MetaOrchestratorStudyResponse)
async def get_milestone_v4_9_meta_orchestrator_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Milestone v4.9 Planetary Cryo-Architecture, Non-Equilibrium Active Matter & Neuromorphic Quantum Bio-Computing OS Grand Meta-Orchestrator Engine study by ID."""
    repo = MilestoneV49MetaOrchestratorRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
