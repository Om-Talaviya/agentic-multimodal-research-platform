"""FastAPI routes for Phase 432: Autonomous Continuous Directed Evolution PACE (Phage-Assisted Continuous Evolution) Fitness Trajectory Modeler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.pace_directed_evolution_trajectory_repo import PaceDirectedEvolutionTrajectoryRepository
from research.orchestration.pace_directed_evolution_trajectory_engine import PaceDirectedEvolutionTrajectoryEngine

router = APIRouter(prefix="/pace-directed-evolution-trajectory", tags=["pace-directed-evolution-trajectory"])


class AnalyzePaceDirectedEvolutionTrajectoryRequest(BaseModel):
    name: str = Field(..., example="Autonomous Continuous Directed Evolution PACE (Phage-Assisted Continuous Evolution) Fitness Trajectory Modeler Run")
    target_specimen: str = Field(default="Continuous Chemostat Lago Lagoon Phage Population")
    analytical_modality: str = Field(default="pace-directed-evolution")
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


class PaceDirectedEvolutionTrajectoryStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    selection_stringency_factor: float
    mutational_drift_velocity_subs_per_hr: float
    fitness_enrichment_trajectory_fold: float
    lagoon_dilution_rate_vol_per_hr: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=PaceDirectedEvolutionTrajectoryStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_pace_directed_evolution_trajectory(
    req: AnalyzePaceDirectedEvolutionTrajectoryRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Continuous Directed Evolution PACE (Phage-Assisted Continuous Evolution) Fitness Trajectory Modeler analysis and persist study."""
    engine = PaceDirectedEvolutionTrajectoryEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = PaceDirectedEvolutionTrajectoryRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        selection_stringency_factor=result.selection_stringency_factor,
        mutational_drift_velocity_subs_per_hr=result.mutational_drift_velocity_subs_per_hr,
        fitness_enrichment_trajectory_fold=result.fitness_enrichment_trajectory_fold,
        lagoon_dilution_rate_vol_per_hr=result.lagoon_dilution_rate_vol_per_hr,
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

    return PaceDirectedEvolutionTrajectoryStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        selection_stringency_factor=study.selection_stringency_factor,
        mutational_drift_velocity_subs_per_hr=study.mutational_drift_velocity_subs_per_hr,
        fitness_enrichment_trajectory_fold=study.fitness_enrichment_trajectory_fold,
        lagoon_dilution_rate_vol_per_hr=study.lagoon_dilution_rate_vol_per_hr,
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


@router.get("/studies", response_model=List[PaceDirectedEvolutionTrajectoryStudyResponse])
async def list_pace_directed_evolution_trajectory_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Continuous Directed Evolution PACE (Phage-Assisted Continuous Evolution) Fitness Trajectory Modeler studies."""
    repo = PaceDirectedEvolutionTrajectoryRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=PaceDirectedEvolutionTrajectoryStudyResponse)
async def get_pace_directed_evolution_trajectory_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Continuous Directed Evolution PACE (Phage-Assisted Continuous Evolution) Fitness Trajectory Modeler study by ID."""
    repo = PaceDirectedEvolutionTrajectoryRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
