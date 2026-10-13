"""FastAPI routes for Phase 455: Autonomous Milestone v4.5 Planetary Nanoscale Biomachines, Quantum Biology & Synthetic Consortia Grand Meta-Orchestrator Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.milestone_v4_5_meta_orchestrator_repo import MilestoneV45MetaOrchestratorRepository
from research.orchestration.milestone_v4_5_meta_orchestrator_engine import MilestoneV45MetaOrchestratorEngine

router = APIRouter(prefix="/milestone-v4-5-meta-orchestrator", tags=["milestone-v4-5-meta-orchestrator"])


class AnalyzeMilestoneV45MetaOrchestratorRequest(BaseModel):
    name: str = Field(..., example="Autonomous Milestone v4.5 Planetary Nanoscale Biomachines, Quantum Biology & Synthetic Consortia Grand Meta-Orchestrator Engine Run")
    target_specimen: str = Field(default="Unified Cross-Domain Multimodal Biosphere Supercomputing Matrix across 21 Research Studios")
    analytical_modality: str = Field(default="milestone-v4-5-planetary-synthesis")
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


class MilestoneV45MetaOrchestratorStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    cross_modality_synthesis_entropy: float
    quantum_biomolecular_convergence_index: float
    consortium_supercomputing_orchestration_score: float
    grand_unification_fidelity_tau: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=MilestoneV45MetaOrchestratorStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_milestone_v4_5_meta_orchestrator(
    req: AnalyzeMilestoneV45MetaOrchestratorRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Milestone v4.5 Planetary Nanoscale Biomachines, Quantum Biology & Synthetic Consortia Grand Meta-Orchestrator Engine analysis and persist study."""
    engine = MilestoneV45MetaOrchestratorEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = MilestoneV45MetaOrchestratorRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        cross_modality_synthesis_entropy=result.cross_modality_synthesis_entropy,
        quantum_biomolecular_convergence_index=result.quantum_biomolecular_convergence_index,
        consortium_supercomputing_orchestration_score=result.consortium_supercomputing_orchestration_score,
        grand_unification_fidelity_tau=result.grand_unification_fidelity_tau,
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

    return MilestoneV45MetaOrchestratorStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        cross_modality_synthesis_entropy=study.cross_modality_synthesis_entropy,
        quantum_biomolecular_convergence_index=study.quantum_biomolecular_convergence_index,
        consortium_supercomputing_orchestration_score=study.consortium_supercomputing_orchestration_score,
        grand_unification_fidelity_tau=study.grand_unification_fidelity_tau,
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


@router.get("/studies", response_model=List[MilestoneV45MetaOrchestratorStudyResponse])
async def list_milestone_v4_5_meta_orchestrator_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Milestone v4.5 Planetary Nanoscale Biomachines, Quantum Biology & Synthetic Consortia Grand Meta-Orchestrator Engine studies."""
    repo = MilestoneV45MetaOrchestratorRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=MilestoneV45MetaOrchestratorStudyResponse)
async def get_milestone_v4_5_meta_orchestrator_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Milestone v4.5 Planetary Nanoscale Biomachines, Quantum Biology & Synthetic Consortia Grand Meta-Orchestrator Engine study by ID."""
    repo = MilestoneV45MetaOrchestratorRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
