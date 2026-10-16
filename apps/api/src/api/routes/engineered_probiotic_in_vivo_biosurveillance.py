"""FastAPI route for Phase 574: Autonomous Engineered Probiotic Gastrointestinal In-Vivo Biosurveillance & Colitis Biomarker Logic Gate Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.engineered_probiotic_in_vivo_biosurveillance_repo import EngineeredProbioticInVivoBiosurveillanceRepository
from research.orchestration.engineered_probiotic_in_vivo_biosurveillance_engine import EngineeredProbioticInVivoBiosurveillanceEngine

router = APIRouter(prefix="/engineered-probiotic-in-vivo-biosurveillance", tags=["Phase 574 - Autonomous Engineered Probiotic Gastrointestinal In-Vivo Biosurveillance & Colitis Biomarker Logic Gate Engine"])


class EngineeredProbioticInVivoBiosurveillanceAnalyzeRequest(BaseModel):
    name: str = Field(default="Autonomous Engineered Probiotic Gastrointestinal In-Vivo Biosurveillance & Colitis Biomarker Logic Gate Engine Study")
    target_specimen: Optional[str] = Field(default="Engineered Escherichia coli Nissle 1917 Dual-Input Nitric Oxide and Tetrathionate Responsive Memory Circuit")
    analytical_modality: Optional[str] = Field(default="probiotic-in-vivo-biosurveillance")
    input_scale: float = Field(default=1.0, ge=0.1, le=10.0)


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


class EngineeredProbioticInVivoBiosurveillanceStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    calprotectin_induction_fold_change: float
    genetic_circuit_retention_stability: float
    gut_colonization_density_cfu_g: float
    false_positive_activation_rate: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []


@router.post("/analyze", response_model=EngineeredProbioticInVivoBiosurveillanceStudyResponse)
async def analyze_engineered_probiotic_in_vivo_biosurveillance(
    req: EngineeredProbioticInVivoBiosurveillanceAnalyzeRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Execute autonomous analysis for Autonomous Engineered Probiotic Gastrointestinal In-Vivo Biosurveillance & Colitis Biomarker Logic Gate Engine."""
    engine = EngineeredProbioticInVivoBiosurveillanceEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = EngineeredProbioticInVivoBiosurveillanceRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        calprotectin_induction_fold_change=result.calprotectin_induction_fold_change,
        genetic_circuit_retention_stability=result.genetic_circuit_retention_stability,
        gut_colonization_density_cfu_g=result.gut_colonization_density_cfu_g,
        false_positive_activation_rate=result.false_positive_activation_rate,
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

    return EngineeredProbioticInVivoBiosurveillanceStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        calprotectin_induction_fold_change=study.calprotectin_induction_fold_change,
        genetic_circuit_retention_stability=study.genetic_circuit_retention_stability,
        gut_colonization_density_cfu_g=study.gut_colonization_density_cfu_g,
        false_positive_activation_rate=study.false_positive_activation_rate,
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


@router.get("/studies", response_model=List[EngineeredProbioticInVivoBiosurveillanceStudyResponse])
async def list_engineered_probiotic_in_vivo_biosurveillance_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Engineered Probiotic Gastrointestinal In-Vivo Biosurveillance & Colitis Biomarker Logic Gate Engine studies."""
    repo = EngineeredProbioticInVivoBiosurveillanceRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=EngineeredProbioticInVivoBiosurveillanceStudyResponse)
async def get_engineered_probiotic_in_vivo_biosurveillance_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Engineered Probiotic Gastrointestinal In-Vivo Biosurveillance & Colitis Biomarker Logic Gate Engine study by ID."""
    repo = EngineeredProbioticInVivoBiosurveillanceRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
