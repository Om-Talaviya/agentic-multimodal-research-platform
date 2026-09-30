"""FastAPI routes for Phase 413: Milestone v4.3 Planetary Frontier Bioscience Multimodal Research OS Grand Synthesis & Meta-Orchestrator Engine Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.milestone_v4_3_meta_orchestrator_repo import MilestoneV43MetaOrchestratorRepository
from research.orchestration.milestone_v4_3_meta_orchestrator_engine import MilestoneV43MetaOrchestratorEngine

router = APIRouter(prefix="/milestone-v4-3-meta-orchestrator", tags=["milestone-v4-3-meta-orchestrator"])


class AnalyzeMilestoneV43MetaOrchestratorRequest(BaseModel):
    name: str = Field(..., example="Autonomous Milestone v4.3 Planetary Frontier Bioscience Multimodal Research OS Grand Synthesis & Meta-Orchestrator Engine Run")
    target_specimen: str = Field(default="Human Patient Cohort Sample")
    analytical_modality: str = Field(default="milestone-v4-3-meta-orchestration")
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


class MilestoneV43MetaOrchestratorStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    global_system_synthesis_coherence_index: float
    cross_modal_autonomous_research_throughput_fold: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=MilestoneV43MetaOrchestratorStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_milestone_v4_3_meta_orchestrator(
    req: AnalyzeMilestoneV43MetaOrchestratorRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Milestone v4.3 Planetary Frontier Bioscience Multimodal Research OS Grand Synthesis & Meta-Orchestrator Engine analysis and persist study record."""
    engine = MilestoneV43MetaOrchestratorEngine()
    analysis = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = MilestoneV43MetaOrchestratorRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=analysis.target_specimen,
        analytical_modality=analysis.analytical_modality,
        global_system_synthesis_coherence_index=getattr(analysis, "global_system_synthesis_coherence_index"),
        cross_modal_autonomous_research_throughput_fold=getattr(analysis, "cross_modal_autonomous_research_throughput_fold"),
        confidence_score=analysis.confidence_score,
        status="completed",
        summary_report=analysis.summary_report,
    )

    for it in analysis.item_profiles:
        await repo.add_item_profile(
            study_id=study.id,
            item_name=it.item_name,
            profile_category=it.profile_category,
            quantitative_value=it.quantitative_value,
            log2_fold_change=it.log2_fold_change,
            significance_score=it.significance_score,
        )

    for tr in analysis.metric_traces:
        await repo.add_metric_trace(
            study_id=study.id,
            metric_dimension=tr.metric_dimension,
            observed_value=tr.observed_value,
            z_score=tr.z_score,
            p_value=tr.p_value,
        )

    return MilestoneV43MetaOrchestratorStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        global_system_synthesis_coherence_index=getattr(study, "global_system_synthesis_coherence_index"),
        cross_modal_autonomous_research_throughput_fold=getattr(study, "cross_modal_autonomous_research_throughput_fold"),
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
            ) for it in analysis.item_profiles
        ],
        metric_traces=[
            MetricTraceResponse(
                metric_dimension=tr.metric_dimension,
                observed_value=tr.observed_value,
                z_score=tr.z_score,
                p_value=tr.p_value,
            ) for tr in analysis.metric_traces
        ],
    )


@router.get("/studies", response_model=List[MilestoneV43MetaOrchestratorStudyResponse])
async def list_milestone_v4_3_meta_orchestrator_studies(
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List historical Milestone v4.3 Planetary Frontier Bioscience Multimodal Research OS Grand Synthesis & Meta-Orchestrator Engine studies."""
    repo = MilestoneV43MetaOrchestratorRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        MilestoneV43MetaOrchestratorStudyResponse(
            id=s.id,
            name=s.name,
            target_specimen=s.target_specimen,
            analytical_modality=s.analytical_modality,
            global_system_synthesis_coherence_index=getattr(s, "global_system_synthesis_coherence_index"),
            cross_modal_autonomous_research_throughput_fold=getattr(s, "cross_modal_autonomous_research_throughput_fold"),
            confidence_score=s.confidence_score,
            status=s.status,
            summary_report=s.summary_report,
            item_profiles=[],
            metric_traces=[],
        ) for s in studies
    ]


@router.get("/studies/{study_id}", response_model=MilestoneV43MetaOrchestratorStudyResponse)
async def get_milestone_v4_3_meta_orchestrator_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve details for a single Milestone v4.3 Planetary Frontier Bioscience Multimodal Research OS Grand Synthesis & Meta-Orchestrator Engine study."""
    repo = MilestoneV43MetaOrchestratorRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")
    return MilestoneV43MetaOrchestratorStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        global_system_synthesis_coherence_index=getattr(study, "global_system_synthesis_coherence_index"),
        cross_modal_autonomous_research_throughput_fold=getattr(study, "cross_modal_autonomous_research_throughput_fold"),
        confidence_score=study.confidence_score,
        status=study.status,
        summary_report=study.summary_report,
        item_profiles=[],
        metric_traces=[],
    )
