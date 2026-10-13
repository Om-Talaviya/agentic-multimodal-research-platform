"""FastAPI routes for Phase 454: Autonomous Synthetic Cell-Free Compartmentalized Gene Circuit Quorum Feedback Oscillator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.cell_free_quorum_feedback_oscillator_repo import CellFreeQuorumFeedbackOscillatorRepository
from research.orchestration.cell_free_quorum_feedback_oscillator_engine import CellFreeQuorumFeedbackOscillatorEngine

router = APIRouter(prefix="/cell-free-quorum-oscillator", tags=["cell-free-quorum-oscillator"])


class AnalyzeCellFreeQuorumFeedbackOscillatorRequest(BaseModel):
    name: str = Field(..., example="Autonomous Synthetic Cell-Free Compartmentalized Gene Circuit Quorum Feedback Oscillator Run")
    target_specimen: str = Field(default="Micro-Emulsion Lipid Vesicles with LuxI/LuxR Synthetic Transcriptional Auto-Inducer Network")
    analytical_modality: str = Field(default="cell-free-quorum-oscillator")
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


class CellFreeQuorumFeedbackOscillatorStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    quorum_oscillation_periodicity_hours: float
    ahl_autoinducer_diffusion_flux_umol_cm2_s: float
    inter_compartment_synchronization_index: float
    circuit_persistence_lifetime_hours: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=CellFreeQuorumFeedbackOscillatorStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_cell_free_quorum_feedback_oscillator(
    req: AnalyzeCellFreeQuorumFeedbackOscillatorRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Synthetic Cell-Free Compartmentalized Gene Circuit Quorum Feedback Oscillator analysis and persist study."""
    engine = CellFreeQuorumFeedbackOscillatorEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = CellFreeQuorumFeedbackOscillatorRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        quorum_oscillation_periodicity_hours=result.quorum_oscillation_periodicity_hours,
        ahl_autoinducer_diffusion_flux_umol_cm2_s=result.ahl_autoinducer_diffusion_flux_umol_cm2_s,
        inter_compartment_synchronization_index=result.inter_compartment_synchronization_index,
        circuit_persistence_lifetime_hours=result.circuit_persistence_lifetime_hours,
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

    return CellFreeQuorumFeedbackOscillatorStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        quorum_oscillation_periodicity_hours=study.quorum_oscillation_periodicity_hours,
        ahl_autoinducer_diffusion_flux_umol_cm2_s=study.ahl_autoinducer_diffusion_flux_umol_cm2_s,
        inter_compartment_synchronization_index=study.inter_compartment_synchronization_index,
        circuit_persistence_lifetime_hours=study.circuit_persistence_lifetime_hours,
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


@router.get("/studies", response_model=List[CellFreeQuorumFeedbackOscillatorStudyResponse])
async def list_cell_free_quorum_feedback_oscillator_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Synthetic Cell-Free Compartmentalized Gene Circuit Quorum Feedback Oscillator studies."""
    repo = CellFreeQuorumFeedbackOscillatorRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=CellFreeQuorumFeedbackOscillatorStudyResponse)
async def get_cell_free_quorum_feedback_oscillator_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Synthetic Cell-Free Compartmentalized Gene Circuit Quorum Feedback Oscillator study by ID."""
    repo = CellFreeQuorumFeedbackOscillatorRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
