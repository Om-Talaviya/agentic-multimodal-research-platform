"""FastAPI routes for Phase 425: Autonomous Cell-Free Protein TX-TL Compartmentalized Microfluidic Logic Oscillator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.cfps_microfluidic_oscillator_repo import CfpsMicrofluidicOscillatorRepository
from research.orchestration.cfps_microfluidic_oscillator_engine import CfpsMicrofluidicOscillatorEngine

router = APIRouter(prefix="/cfps-microfluidic-oscillator", tags=["cfps-microfluidic-oscillator"])


class AnalyzeCfpsMicrofluidicOscillatorRequest(BaseModel):
    name: str = Field(..., example="Autonomous Cell-Free Protein TX-TL Compartmentalized Microfluidic Logic Oscillator Run")
    target_specimen: str = Field(default="Microfluidic Droplet Array with Repressilator TX-TL Reaction")
    analytical_modality: str = Field(default="cfps-microfluidic-oscillator")
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


class CfpsMicrofluidicOscillatorStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    oscillation_period_minutes: float
    fluorescent_reporter_amplitude_rfu: float
    reaction_dwell_stability_score: float
    damping_decay_coefficient: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=CfpsMicrofluidicOscillatorStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_cfps_microfluidic_oscillator(
    req: AnalyzeCfpsMicrofluidicOscillatorRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Cell-Free Protein TX-TL Compartmentalized Microfluidic Logic Oscillator analysis and persist study."""
    engine = CfpsMicrofluidicOscillatorEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = CfpsMicrofluidicOscillatorRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        oscillation_period_minutes=result.oscillation_period_minutes,
        fluorescent_reporter_amplitude_rfu=result.fluorescent_reporter_amplitude_rfu,
        reaction_dwell_stability_score=result.reaction_dwell_stability_score,
        damping_decay_coefficient=result.damping_decay_coefficient,
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

    return CfpsMicrofluidicOscillatorStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        oscillation_period_minutes=study.oscillation_period_minutes,
        fluorescent_reporter_amplitude_rfu=study.fluorescent_reporter_amplitude_rfu,
        reaction_dwell_stability_score=study.reaction_dwell_stability_score,
        damping_decay_coefficient=study.damping_decay_coefficient,
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


@router.get("/studies", response_model=List[CfpsMicrofluidicOscillatorStudyResponse])
async def list_cfps_microfluidic_oscillator_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Cell-Free Protein TX-TL Compartmentalized Microfluidic Logic Oscillator studies."""
    repo = CfpsMicrofluidicOscillatorRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=CfpsMicrofluidicOscillatorStudyResponse)
async def get_cfps_microfluidic_oscillator_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Cell-Free Protein TX-TL Compartmentalized Microfluidic Logic Oscillator study by ID."""
    repo = CfpsMicrofluidicOscillatorRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
