"""FastAPI routes for Phase 470: Autonomous Bio-Piezoelectric Collagen Matrix Electromechanical Transduction Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.piezoelectric_collagen_matrix_transduction_repo import PiezoelectricCollagenMatrixTransductionRepository
from research.orchestration.piezoelectric_collagen_matrix_transduction_engine import PiezoelectricCollagenMatrixTransductionEngine

router = APIRouter(prefix="/piezoelectric-collagen-transduction", tags=["piezoelectric-collagen-transduction"])


class AnalyzePiezoelectricCollagenMatrixTransductionRequest(BaseModel):
    name: str = Field(..., example="Autonomous Bio-Piezoelectric Collagen Matrix Electromechanical Transduction Engine Run")
    target_specimen: str = Field(default="Dense Fibrillar Type-I Collagen Fascicle Scaffold with Applied High-Frequency Axial Dynamic Strain")
    analytical_modality: str = Field(default="piezoelectric-collagen-transduction")
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


class PiezoelectricCollagenMatrixTransductionStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    piezoelectric_coefficient_d33_pC_per_N: float
    surface_potential_streaming_voltage_mV: float
    dynamic_electromechanical_coupling_factor: float
    osteogenic_mineralization_acceleration_index: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=PiezoelectricCollagenMatrixTransductionStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_piezoelectric_collagen_matrix_transduction(
    req: AnalyzePiezoelectricCollagenMatrixTransductionRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Bio-Piezoelectric Collagen Matrix Electromechanical Transduction Engine analysis and persist study."""
    engine = PiezoelectricCollagenMatrixTransductionEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = PiezoelectricCollagenMatrixTransductionRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        piezoelectric_coefficient_d33_pC_per_N=result.piezoelectric_coefficient_d33_pC_per_N,
        surface_potential_streaming_voltage_mV=result.surface_potential_streaming_voltage_mV,
        dynamic_electromechanical_coupling_factor=result.dynamic_electromechanical_coupling_factor,
        osteogenic_mineralization_acceleration_index=result.osteogenic_mineralization_acceleration_index,
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

    return PiezoelectricCollagenMatrixTransductionStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        piezoelectric_coefficient_d33_pC_per_N=study.piezoelectric_coefficient_d33_pC_per_N,
        surface_potential_streaming_voltage_mV=study.surface_potential_streaming_voltage_mV,
        dynamic_electromechanical_coupling_factor=study.dynamic_electromechanical_coupling_factor,
        osteogenic_mineralization_acceleration_index=study.osteogenic_mineralization_acceleration_index,
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


@router.get("/studies", response_model=List[PiezoelectricCollagenMatrixTransductionStudyResponse])
async def list_piezoelectric_collagen_matrix_transduction_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Bio-Piezoelectric Collagen Matrix Electromechanical Transduction Engine studies."""
    repo = PiezoelectricCollagenMatrixTransductionRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=PiezoelectricCollagenMatrixTransductionStudyResponse)
async def get_piezoelectric_collagen_matrix_transduction_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Bio-Piezoelectric Collagen Matrix Electromechanical Transduction Engine study by ID."""
    repo = PiezoelectricCollagenMatrixTransductionRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
