"""FastAPI routes for Phase 556: Autonomous Synthetic Mammalian Gene Circuit Feedback Integral Controller for Homeostatic Glucose Regulation."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.mammalian_gene_circuit_homeostatic_controller_repo import MammalianGeneCircuitHomeostaticControllerRepository
from research.orchestration.mammalian_gene_circuit_homeostatic_controller_engine import MammalianGeneCircuitHomeostaticControllerEngine

router = APIRouter(prefix="/mammalian-gene-circuit-homeostatic-controller", tags=["mammalian-gene-circuit-homeostatic-controller"])


class AnalyzeMammalianGeneCircuitHomeostaticControllerRequest(BaseModel):
    name: str = Field(..., example="Autonomous Synthetic Mammalian Gene Circuit Feedback Integral Controller for Homeostatic Glucose Regulation Run")
    target_specimen: str = Field(default="Engineered Beta-Cell Like HEK-293T cells expressing Synthetic Glucose-Sensing Integral Antithetic Feedback Invertible Controller")
    analytical_modality: str = Field(default="synthetic-homeostatic-circuit")
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


class MammalianGeneCircuitHomeostaticControllerStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    homeostatic_glucose_setpoint_steady_state_mg_dl: float
    integral_control_settling_time_minutes: float
    steady_state_error_offset_pct: float
    insulin_secretion_burst_amplitude_pg_cell: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=MammalianGeneCircuitHomeostaticControllerStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_mammalian_gene_circuit_homeostatic_controller(
    req: AnalyzeMammalianGeneCircuitHomeostaticControllerRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Synthetic Mammalian Gene Circuit Feedback Integral Controller for Homeostatic Glucose Regulation analysis and persist study."""
    engine = MammalianGeneCircuitHomeostaticControllerEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = MammalianGeneCircuitHomeostaticControllerRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        homeostatic_glucose_setpoint_steady_state_mg_dl=result.homeostatic_glucose_setpoint_steady_state_mg_dl,
        integral_control_settling_time_minutes=result.integral_control_settling_time_minutes,
        steady_state_error_offset_pct=result.steady_state_error_offset_pct,
        insulin_secretion_burst_amplitude_pg_cell=result.insulin_secretion_burst_amplitude_pg_cell,
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

    return MammalianGeneCircuitHomeostaticControllerStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        homeostatic_glucose_setpoint_steady_state_mg_dl=study.homeostatic_glucose_setpoint_steady_state_mg_dl,
        integral_control_settling_time_minutes=study.integral_control_settling_time_minutes,
        steady_state_error_offset_pct=study.steady_state_error_offset_pct,
        insulin_secretion_burst_amplitude_pg_cell=study.insulin_secretion_burst_amplitude_pg_cell,
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


@router.get("/studies", response_model=List[MammalianGeneCircuitHomeostaticControllerStudyResponse])
async def list_mammalian_gene_circuit_homeostatic_controller_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Synthetic Mammalian Gene Circuit Feedback Integral Controller for Homeostatic Glucose Regulation studies."""
    repo = MammalianGeneCircuitHomeostaticControllerRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=MammalianGeneCircuitHomeostaticControllerStudyResponse)
async def get_mammalian_gene_circuit_homeostatic_controller_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Synthetic Mammalian Gene Circuit Feedback Integral Controller for Homeostatic Glucose Regulation study by ID."""
    repo = MammalianGeneCircuitHomeostaticControllerRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
