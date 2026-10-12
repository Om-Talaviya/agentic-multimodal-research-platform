"""FastAPI routes for Phase 419: Autonomous In-Cell NMR Macromolecular Crowding & Chemical Shift Perturbation Tensor Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.in_cell_nmr_crowding_tensor_repo import InCellNmrCrowdingTensorRepository
from research.orchestration.in_cell_nmr_crowding_tensor_engine import InCellNmrCrowdingTensorEngine

router = APIRouter(prefix="/in-cell-nmr-crowding-tensor", tags=["in-cell-nmr-crowding-tensor"])


class AnalyzeInCellNmrCrowdingTensorRequest(BaseModel):
    name: str = Field(..., example="Autonomous In-Cell NMR Macromolecular Crowding & Chemical Shift Perturbation Tensor Engine Run")
    target_specimen: str = Field(default="15N/13C-Enriched Intact E. coli Cytoplasm with Model Protein")
    analytical_modality: str = Field(default="in-cell-nmr")
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


class InCellNmrCrowdingTensorStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    chemical_shift_perturbation_ppm: float
    rotational_correlation_time_ns: float
    crowding_viscosity_factor: float
    transverse_relaxation_r2_rate: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=InCellNmrCrowdingTensorStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_in_cell_nmr_crowding_tensor(
    req: AnalyzeInCellNmrCrowdingTensorRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous In-Cell NMR Macromolecular Crowding & Chemical Shift Perturbation Tensor Engine analysis and persist study."""
    engine = InCellNmrCrowdingTensorEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = InCellNmrCrowdingTensorRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        chemical_shift_perturbation_ppm=result.chemical_shift_perturbation_ppm,
        rotational_correlation_time_ns=result.rotational_correlation_time_ns,
        crowding_viscosity_factor=result.crowding_viscosity_factor,
        transverse_relaxation_r2_rate=result.transverse_relaxation_r2_rate,
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

    return InCellNmrCrowdingTensorStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        chemical_shift_perturbation_ppm=study.chemical_shift_perturbation_ppm,
        rotational_correlation_time_ns=study.rotational_correlation_time_ns,
        crowding_viscosity_factor=study.crowding_viscosity_factor,
        transverse_relaxation_r2_rate=study.transverse_relaxation_r2_rate,
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


@router.get("/studies", response_model=List[InCellNmrCrowdingTensorStudyResponse])
async def list_in_cell_nmr_crowding_tensor_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous In-Cell NMR Macromolecular Crowding & Chemical Shift Perturbation Tensor Engine studies."""
    repo = InCellNmrCrowdingTensorRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=InCellNmrCrowdingTensorStudyResponse)
async def get_in_cell_nmr_crowding_tensor_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous In-Cell NMR Macromolecular Crowding & Chemical Shift Perturbation Tensor Engine study by ID."""
    repo = InCellNmrCrowdingTensorRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
