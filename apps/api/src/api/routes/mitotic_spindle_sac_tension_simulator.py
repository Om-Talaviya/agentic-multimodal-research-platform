"""FastAPI routes for Phase 452: Autonomous Microtubule Spindle Assembly Checkpoint (SAC) Mitotic Tension Kinetic Simulator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.mitotic_spindle_sac_tension_simulator_repo import MitoticSpindleSacTensionRepository
from research.orchestration.mitotic_spindle_sac_tension_simulator_engine import MitoticSpindleSacTensionEngine

router = APIRouter(prefix="/mitotic-spindle-sac-tension", tags=["mitotic-spindle-sac-tension"])


class AnalyzeMitoticSpindleSacTensionRequest(BaseModel):
    name: str = Field(..., example="Autonomous Microtubule Spindle Assembly Checkpoint (SAC) Mitotic Tension Kinetic Simulator Run")
    target_specimen: str = Field(default="Bipolar Mitotic Kinetochore-Microtubule Interface with Mad2/BubR1 Checkpoint Sensor")
    analytical_modality: str = Field(default="spindle-assembly-sac-kinetics")
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


class MitoticSpindleSacTensionStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    kinetochore_tension_pico_newtons: float
    mad2_activation_rate_constant_s_inv: float
    anaphase_onset_delay_minutes: float
    spindle_bipolar_alignment_coherence: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=MitoticSpindleSacTensionStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_mitotic_spindle_sac_tension_simulator(
    req: AnalyzeMitoticSpindleSacTensionRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Microtubule Spindle Assembly Checkpoint (SAC) Mitotic Tension Kinetic Simulator analysis and persist study."""
    engine = MitoticSpindleSacTensionEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = MitoticSpindleSacTensionRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        kinetochore_tension_pico_newtons=result.kinetochore_tension_pico_newtons,
        mad2_activation_rate_constant_s_inv=result.mad2_activation_rate_constant_s_inv,
        anaphase_onset_delay_minutes=result.anaphase_onset_delay_minutes,
        spindle_bipolar_alignment_coherence=result.spindle_bipolar_alignment_coherence,
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

    return MitoticSpindleSacTensionStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        kinetochore_tension_pico_newtons=study.kinetochore_tension_pico_newtons,
        mad2_activation_rate_constant_s_inv=study.mad2_activation_rate_constant_s_inv,
        anaphase_onset_delay_minutes=study.anaphase_onset_delay_minutes,
        spindle_bipolar_alignment_coherence=study.spindle_bipolar_alignment_coherence,
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


@router.get("/studies", response_model=List[MitoticSpindleSacTensionStudyResponse])
async def list_mitotic_spindle_sac_tension_simulator_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Microtubule Spindle Assembly Checkpoint (SAC) Mitotic Tension Kinetic Simulator studies."""
    repo = MitoticSpindleSacTensionRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=MitoticSpindleSacTensionStudyResponse)
async def get_mitotic_spindle_sac_tension_simulator_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Microtubule Spindle Assembly Checkpoint (SAC) Mitotic Tension Kinetic Simulator study by ID."""
    repo = MitoticSpindleSacTensionRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
