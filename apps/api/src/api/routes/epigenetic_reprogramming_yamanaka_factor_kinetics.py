"""FastAPI routes for Phase 546: Autonomous Stochastic Pioneer Transcription Factor Yamanaka Reprogramming Trajectory Predictor."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.epigenetic_reprogramming_yamanaka_factor_kinetics_repo import EpigeneticReprogrammingYamanakaFactorKineticsRepository
from research.orchestration.epigenetic_reprogramming_yamanaka_factor_kinetics_engine import EpigeneticReprogrammingYamanakaFactorKineticsEngine

router = APIRouter(prefix="/epigenetic-reprogramming-yamanaka-factor-kinetics", tags=["epigenetic-reprogramming-yamanaka-factor-kinetics"])


class AnalyzeEpigeneticReprogrammingYamanakaFactorKineticsRequest(BaseModel):
    name: str = Field(..., example="Autonomous Stochastic Pioneer Transcription Factor Yamanaka Reprogramming Trajectory Predictor Run")
    target_specimen: str = Field(default="Single-Cell Doxycycline-Inducible OSKM Human Dermal Fibroblasts tracked across 21 Days")
    analytical_modality: str = Field(default="yamanaka-reprogramming-kinetics")
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


class EpigeneticReprogrammingYamanakaFactorKineticsStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    fully_reprogrammed_naive_pluripotency_rate_pct: float
    oct4_sox2_pioneer_chromatin_dwell_time_s: float
    dna_methylation_clock_reversal_years: float
    trajectory_waddington_barrier_crossing_prob: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=EpigeneticReprogrammingYamanakaFactorKineticsStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_epigenetic_reprogramming_yamanaka_factor_kinetics(
    req: AnalyzeEpigeneticReprogrammingYamanakaFactorKineticsRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Stochastic Pioneer Transcription Factor Yamanaka Reprogramming Trajectory Predictor analysis and persist study."""
    engine = EpigeneticReprogrammingYamanakaFactorKineticsEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = EpigeneticReprogrammingYamanakaFactorKineticsRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        fully_reprogrammed_naive_pluripotency_rate_pct=result.fully_reprogrammed_naive_pluripotency_rate_pct,
        oct4_sox2_pioneer_chromatin_dwell_time_s=result.oct4_sox2_pioneer_chromatin_dwell_time_s,
        dna_methylation_clock_reversal_years=result.dna_methylation_clock_reversal_years,
        trajectory_waddington_barrier_crossing_prob=result.trajectory_waddington_barrier_crossing_prob,
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

    return EpigeneticReprogrammingYamanakaFactorKineticsStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        fully_reprogrammed_naive_pluripotency_rate_pct=study.fully_reprogrammed_naive_pluripotency_rate_pct,
        oct4_sox2_pioneer_chromatin_dwell_time_s=study.oct4_sox2_pioneer_chromatin_dwell_time_s,
        dna_methylation_clock_reversal_years=study.dna_methylation_clock_reversal_years,
        trajectory_waddington_barrier_crossing_prob=study.trajectory_waddington_barrier_crossing_prob,
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


@router.get("/studies", response_model=List[EpigeneticReprogrammingYamanakaFactorKineticsStudyResponse])
async def list_epigenetic_reprogramming_yamanaka_factor_kinetics_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Stochastic Pioneer Transcription Factor Yamanaka Reprogramming Trajectory Predictor studies."""
    repo = EpigeneticReprogrammingYamanakaFactorKineticsRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=EpigeneticReprogrammingYamanakaFactorKineticsStudyResponse)
async def get_epigenetic_reprogramming_yamanaka_factor_kinetics_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Stochastic Pioneer Transcription Factor Yamanaka Reprogramming Trajectory Predictor study by ID."""
    repo = EpigeneticReprogrammingYamanakaFactorKineticsRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
