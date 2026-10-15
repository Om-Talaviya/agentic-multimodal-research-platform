"""FastAPI routes for Phase 531: Autonomous Spatially-Resolved Optogenetic Mitochondrial Calcium Spark & Bioenergetics Modeler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.optogenetic_mitochondrial_calcium_oscillator_repo import OptogeneticMitochondrialCalciumOscillatorRepository
from research.orchestration.optogenetic_mitochondrial_calcium_oscillator_engine import OptogeneticMitochondrialCalciumOscillatorEngine

router = APIRouter(prefix="/optogenetic-mitochondrial-calcium-oscillator", tags=["optogenetic-mitochondrial-calcium-oscillator"])


class AnalyzeOptogeneticMitochondrialCalciumOscillatorRequest(BaseModel):
    name: str = Field(..., example="Autonomous Spatially-Resolved Optogenetic Mitochondrial Calcium Spark & Bioenergetics Modeler Run")
    target_specimen: str = Field(default="Human Cardiomyocyte Syncytium with Mitochondrially-Targeted ChR2 and R-GECO1 Probes")
    analytical_modality: str = Field(default="optogenetic-mitochondrial-calcium")
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


class OptogeneticMitochondrialCalciumOscillatorStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    matrix_calcium_influx_rate_uM_per_s: float
    mcu_channel_open_probability: float
    atp_production_coupling_gain_pct: float
    mptp_opening_prevention_threshold_uM: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=OptogeneticMitochondrialCalciumOscillatorStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_optogenetic_mitochondrial_calcium_oscillator(
    req: AnalyzeOptogeneticMitochondrialCalciumOscillatorRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Spatially-Resolved Optogenetic Mitochondrial Calcium Spark & Bioenergetics Modeler analysis and persist study."""
    engine = OptogeneticMitochondrialCalciumOscillatorEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = OptogeneticMitochondrialCalciumOscillatorRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        matrix_calcium_influx_rate_uM_per_s=result.matrix_calcium_influx_rate_uM_per_s,
        mcu_channel_open_probability=result.mcu_channel_open_probability,
        atp_production_coupling_gain_pct=result.atp_production_coupling_gain_pct,
        mptp_opening_prevention_threshold_uM=result.mptp_opening_prevention_threshold_uM,
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

    return OptogeneticMitochondrialCalciumOscillatorStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        matrix_calcium_influx_rate_uM_per_s=study.matrix_calcium_influx_rate_uM_per_s,
        mcu_channel_open_probability=study.mcu_channel_open_probability,
        atp_production_coupling_gain_pct=study.atp_production_coupling_gain_pct,
        mptp_opening_prevention_threshold_uM=study.mptp_opening_prevention_threshold_uM,
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


@router.get("/studies", response_model=List[OptogeneticMitochondrialCalciumOscillatorStudyResponse])
async def list_optogenetic_mitochondrial_calcium_oscillator_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Spatially-Resolved Optogenetic Mitochondrial Calcium Spark & Bioenergetics Modeler studies."""
    repo = OptogeneticMitochondrialCalciumOscillatorRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=OptogeneticMitochondrialCalciumOscillatorStudyResponse)
async def get_optogenetic_mitochondrial_calcium_oscillator_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Spatially-Resolved Optogenetic Mitochondrial Calcium Spark & Bioenergetics Modeler study by ID."""
    repo = OptogeneticMitochondrialCalciumOscillatorRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
