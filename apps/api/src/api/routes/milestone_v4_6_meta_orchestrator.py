"""FastAPI routes for Phase 476: Autonomous Milestone v4.6 Planetary Synthetic Morphogenesis, Biohybrid Cybernetics & Multicellular OS Grand Meta-Orchestrator Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.milestone_v4_6_meta_orchestrator_repo import MilestoneV46MetaOrchestratorRepository
from research.orchestration.milestone_v4_6_meta_orchestrator_engine import MilestoneV46MetaOrchestratorEngine

router = APIRouter(prefix="/milestone-v4-6-meta-orchestrator", tags=["milestone-v4-6-meta-orchestrator"])


class AnalyzeMilestoneV46MetaOrchestratorRequest(BaseModel):
    name: str = Field(..., example="Autonomous Milestone v4.6 Planetary Synthetic Morphogenesis, Biohybrid Cybernetics & Multicellular OS Grand Meta-Orchestrator Engine Run")
    target_specimen: str = Field(default="Integrated Milestone v4.6 Multi-Tissue Synthetic Morphogenesis, Biohybrid Soft Cybernetics & Multicellular Engine Suite")
    analytical_modality: str = Field(default="planetary-v4-6-meta-orchestration")
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


class MilestoneV46MetaOrchestratorStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    multicellular_morphogenesis_coherence_index: float
    biohybrid_actuation_cybernetic_sync_tau: float
    cross_engine_federated_convergence_ratio: float
    global_synthesis_confidence_score: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=MilestoneV46MetaOrchestratorStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_milestone_v4_6_meta_orchestrator(
    req: AnalyzeMilestoneV46MetaOrchestratorRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Milestone v4.6 Planetary Synthetic Morphogenesis, Biohybrid Cybernetics & Multicellular OS Grand Meta-Orchestrator Engine analysis and persist study."""
    engine = MilestoneV46MetaOrchestratorEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = MilestoneV46MetaOrchestratorRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        multicellular_morphogenesis_coherence_index=result.multicellular_morphogenesis_coherence_index,
        biohybrid_actuation_cybernetic_sync_tau=result.biohybrid_actuation_cybernetic_sync_tau,
        cross_engine_federated_convergence_ratio=result.cross_engine_federated_convergence_ratio,
        global_synthesis_confidence_score=result.global_synthesis_confidence_score,
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

    return MilestoneV46MetaOrchestratorStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        multicellular_morphogenesis_coherence_index=study.multicellular_morphogenesis_coherence_index,
        biohybrid_actuation_cybernetic_sync_tau=study.biohybrid_actuation_cybernetic_sync_tau,
        cross_engine_federated_convergence_ratio=study.cross_engine_federated_convergence_ratio,
        global_synthesis_confidence_score=study.global_synthesis_confidence_score,
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


@router.get("/studies", response_model=List[MilestoneV46MetaOrchestratorStudyResponse])
async def list_milestone_v4_6_meta_orchestrator_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Milestone v4.6 Planetary Synthetic Morphogenesis, Biohybrid Cybernetics & Multicellular OS Grand Meta-Orchestrator Engine studies."""
    repo = MilestoneV46MetaOrchestratorRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=MilestoneV46MetaOrchestratorStudyResponse)
async def get_milestone_v4_6_meta_orchestrator_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Milestone v4.6 Planetary Synthetic Morphogenesis, Biohybrid Cybernetics & Multicellular OS Grand Meta-Orchestrator Engine study by ID."""
    repo = MilestoneV46MetaOrchestratorRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
