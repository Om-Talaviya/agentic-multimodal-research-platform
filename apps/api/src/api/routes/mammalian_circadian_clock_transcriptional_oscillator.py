"""FastAPI routes for Phase 442: Autonomous Mammalian Circadian Transcriptional-Translational Feedback Loop (TTFL) Limit Cycle Simulator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.mammalian_circadian_clock_transcriptional_oscillator_repo import MammalianCircadianClockRepository
from research.orchestration.mammalian_circadian_clock_transcriptional_oscillator_engine import MammalianCircadianClockEngine

router = APIRouter(prefix="/mammalian-circadian-clock", tags=["mammalian-circadian-clock"])


class AnalyzeMammalianCircadianClockRequest(BaseModel):
    name: str = Field(..., example="Autonomous Mammalian Circadian Transcriptional-Translational Feedback Loop (TTFL) Limit Cycle Simulator Run")
    target_specimen: str = Field(default="Suprachiasmatic Nucleus (SCN) Single-Cell CLOCK:BMAL1 / PER:CRY Pacemaker Circuit")
    analytical_modality: str = Field(default="circadian-ttfl-oscillator")
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


class MammalianCircadianClockStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    free_running_period_tau_hours: float
    oscillation_amplitude_per2_mrna_ratio: float
    phase_response_shift_hours: float
    limit_cycle_bifurcation_stability: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=MammalianCircadianClockStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_mammalian_circadian_clock_transcriptional_oscillator(
    req: AnalyzeMammalianCircadianClockRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Mammalian Circadian Transcriptional-Translational Feedback Loop (TTFL) Limit Cycle Simulator analysis and persist study."""
    engine = MammalianCircadianClockEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = MammalianCircadianClockRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        free_running_period_tau_hours=result.free_running_period_tau_hours,
        oscillation_amplitude_per2_mrna_ratio=result.oscillation_amplitude_per2_mrna_ratio,
        phase_response_shift_hours=result.phase_response_shift_hours,
        limit_cycle_bifurcation_stability=result.limit_cycle_bifurcation_stability,
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

    return MammalianCircadianClockStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        free_running_period_tau_hours=study.free_running_period_tau_hours,
        oscillation_amplitude_per2_mrna_ratio=study.oscillation_amplitude_per2_mrna_ratio,
        phase_response_shift_hours=study.phase_response_shift_hours,
        limit_cycle_bifurcation_stability=study.limit_cycle_bifurcation_stability,
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


@router.get("/studies", response_model=List[MammalianCircadianClockStudyResponse])
async def list_mammalian_circadian_clock_transcriptional_oscillator_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Mammalian Circadian Transcriptional-Translational Feedback Loop (TTFL) Limit Cycle Simulator studies."""
    repo = MammalianCircadianClockRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=MammalianCircadianClockStudyResponse)
async def get_mammalian_circadian_clock_transcriptional_oscillator_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Mammalian Circadian Transcriptional-Translational Feedback Loop (TTFL) Limit Cycle Simulator study by ID."""
    repo = MammalianCircadianClockRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
