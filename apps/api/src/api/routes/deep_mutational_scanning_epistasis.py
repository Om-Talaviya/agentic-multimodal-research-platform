"""FastAPI routes for Phase 424: Autonomous Deep Mutational Scanning (DMS) Variant Fitness & Thermostability Epistasis Forecaster."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.deep_mutational_scanning_epistasis_repo import DeepMutationalScanningEpistasisRepository
from research.orchestration.deep_mutational_scanning_epistasis_engine import DeepMutationalScanningEpistasisEngine

router = APIRouter(prefix="/deep-mutational-scanning-epistasis", tags=["deep-mutational-scanning-epistasis"])


class AnalyzeDeepMutationalScanningEpistasisRequest(BaseModel):
    name: str = Field(..., example="Autonomous Deep Mutational Scanning (DMS) Variant Fitness & Thermostability Epistasis Forecaster Run")
    target_specimen: str = Field(default="Beta-Lactamase All-Combinatorial Single/Double Point Mutants")
    analytical_modality: str = Field(default="dms-epistasis")
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


class DeepMutationalScanningEpistasisStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    higher_order_epistasis_coefficient: float
    relative_fitness_enrichment_ratio: float
    delta_delta_g_unfolding_kcal: float
    catalytic_efficiency_retention: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=DeepMutationalScanningEpistasisStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_deep_mutational_scanning_epistasis(
    req: AnalyzeDeepMutationalScanningEpistasisRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Deep Mutational Scanning (DMS) Variant Fitness & Thermostability Epistasis Forecaster analysis and persist study."""
    engine = DeepMutationalScanningEpistasisEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = DeepMutationalScanningEpistasisRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        higher_order_epistasis_coefficient=result.higher_order_epistasis_coefficient,
        relative_fitness_enrichment_ratio=result.relative_fitness_enrichment_ratio,
        delta_delta_g_unfolding_kcal=result.delta_delta_g_unfolding_kcal,
        catalytic_efficiency_retention=result.catalytic_efficiency_retention,
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

    return DeepMutationalScanningEpistasisStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        higher_order_epistasis_coefficient=study.higher_order_epistasis_coefficient,
        relative_fitness_enrichment_ratio=study.relative_fitness_enrichment_ratio,
        delta_delta_g_unfolding_kcal=study.delta_delta_g_unfolding_kcal,
        catalytic_efficiency_retention=study.catalytic_efficiency_retention,
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


@router.get("/studies", response_model=List[DeepMutationalScanningEpistasisStudyResponse])
async def list_deep_mutational_scanning_epistasis_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Deep Mutational Scanning (DMS) Variant Fitness & Thermostability Epistasis Forecaster studies."""
    repo = DeepMutationalScanningEpistasisRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=DeepMutationalScanningEpistasisStudyResponse)
async def get_deep_mutational_scanning_epistasis_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Deep Mutational Scanning (DMS) Variant Fitness & Thermostability Epistasis Forecaster study by ID."""
    repo = DeepMutationalScanningEpistasisRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
