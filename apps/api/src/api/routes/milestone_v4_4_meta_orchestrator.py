"""FastAPI routes for Phase 434: Autonomous Milestone v4.4 Planetary Frontier Bioscience Multimodal Research OS Grand Synthesis & Meta-Orchestrator Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.milestone_v4_4_meta_orchestrator_repo import MilestoneV44MetaOrchestratorRepository
from research.orchestration.milestone_v4_4_meta_orchestrator_engine import MilestoneV44MetaOrchestratorEngine

router = APIRouter(prefix="/milestone-v4-4-meta-orchestrator", tags=["milestone-v4-4-meta-orchestrator"])


class AnalyzeMilestoneV44MetaOrchestratorRequest(BaseModel):
    name: str = Field(..., example="Autonomous Milestone v4.4 Planetary Frontier Bioscience Multimodal Research OS Grand Synthesis & Meta-Orchestrator Engine Run")
    target_specimen: str = Field(default="Planetary Multi-Scale Biophysical & Epitranscriptomic Synthesis Consortium")
    analytical_modality: str = Field(default="milestone-v4-4-meta-orchestrator")
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


class MilestoneV44MetaOrchestratorStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    cross_phase_coherence_index: float
    dag_pipeline_throughput_jobs_per_s: float
    multi_modal_synthesis_confidence: float
    autonomous_discovery_convergence_tau: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=MilestoneV44MetaOrchestratorStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_milestone_v4_4_meta_orchestrator(
    req: AnalyzeMilestoneV44MetaOrchestratorRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Milestone v4.4 Planetary Frontier Bioscience Multimodal Research OS Grand Synthesis & Meta-Orchestrator Engine analysis and persist study."""
    engine = MilestoneV44MetaOrchestratorEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = MilestoneV44MetaOrchestratorRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        cross_phase_coherence_index=result.cross_phase_coherence_index,
        dag_pipeline_throughput_jobs_per_s=result.dag_pipeline_throughput_jobs_per_s,
        multi_modal_synthesis_confidence=result.multi_modal_synthesis_confidence,
        autonomous_discovery_convergence_tau=result.autonomous_discovery_convergence_tau,
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

    return MilestoneV44MetaOrchestratorStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        cross_phase_coherence_index=study.cross_phase_coherence_index,
        dag_pipeline_throughput_jobs_per_s=study.dag_pipeline_throughput_jobs_per_s,
        multi_modal_synthesis_confidence=study.multi_modal_synthesis_confidence,
        autonomous_discovery_convergence_tau=study.autonomous_discovery_convergence_tau,
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


@router.get("/studies", response_model=List[MilestoneV44MetaOrchestratorStudyResponse])
async def list_milestone_v4_4_meta_orchestrator_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Milestone v4.4 Planetary Frontier Bioscience Multimodal Research OS Grand Synthesis & Meta-Orchestrator Engine studies."""
    repo = MilestoneV44MetaOrchestratorRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=MilestoneV44MetaOrchestratorStudyResponse)
async def get_milestone_v4_4_meta_orchestrator_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Milestone v4.4 Planetary Frontier Bioscience Multimodal Research OS Grand Synthesis & Meta-Orchestrator Engine study by ID."""
    repo = MilestoneV44MetaOrchestratorRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
