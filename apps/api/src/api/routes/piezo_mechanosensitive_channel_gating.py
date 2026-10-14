"""FastAPI routes for Phase 494: Autonomous Mechanosensitive Ion Channel PIEZO1 Gating & Membrane Tension Indentation Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.piezo_mechanosensitive_channel_gating_repo import PiezoMechanosensitiveChannelGatingRepository
from research.orchestration.piezo_mechanosensitive_channel_gating_engine import PiezoMechanosensitiveChannelGatingEngine

router = APIRouter(prefix="/piezo-mechanosensitive-channel-gating", tags=["piezo-mechanosensitive-channel-gating"])


class AnalyzePiezoMechanosensitiveChannelGatingRequest(BaseModel):
    name: str = Field(..., example="Autonomous Mechanosensitive Ion Channel PIEZO1 Gating & Membrane Tension Indentation Engine Run")
    target_specimen: str = Field(default="High-Speed Pressure Clamped HEK293 Cell expressing Human PIEZO1 Trimeric Propeller Blades")
    analytical_modality: str = Field(default="piezo-mechanosensitive-gating")
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


class PiezoMechanosensitiveChannelGatingStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    half_maximal_activation_tension_mN_per_m: float
    channel_open_probability_p_open: float
    single_channel_conductance_pS: float
    mechanical_inactivation_tau_ms: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=PiezoMechanosensitiveChannelGatingStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_piezo_mechanosensitive_channel_gating(
    req: AnalyzePiezoMechanosensitiveChannelGatingRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Mechanosensitive Ion Channel PIEZO1 Gating & Membrane Tension Indentation Engine analysis and persist study."""
    engine = PiezoMechanosensitiveChannelGatingEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = PiezoMechanosensitiveChannelGatingRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        half_maximal_activation_tension_mN_per_m=result.half_maximal_activation_tension_mN_per_m,
        channel_open_probability_p_open=result.channel_open_probability_p_open,
        single_channel_conductance_pS=result.single_channel_conductance_pS,
        mechanical_inactivation_tau_ms=result.mechanical_inactivation_tau_ms,
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

    return PiezoMechanosensitiveChannelGatingStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        half_maximal_activation_tension_mN_per_m=study.half_maximal_activation_tension_mN_per_m,
        channel_open_probability_p_open=study.channel_open_probability_p_open,
        single_channel_conductance_pS=study.single_channel_conductance_pS,
        mechanical_inactivation_tau_ms=study.mechanical_inactivation_tau_ms,
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


@router.get("/studies", response_model=List[PiezoMechanosensitiveChannelGatingStudyResponse])
async def list_piezo_mechanosensitive_channel_gating_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Mechanosensitive Ion Channel PIEZO1 Gating & Membrane Tension Indentation Engine studies."""
    repo = PiezoMechanosensitiveChannelGatingRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=PiezoMechanosensitiveChannelGatingStudyResponse)
async def get_piezo_mechanosensitive_channel_gating_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Mechanosensitive Ion Channel PIEZO1 Gating & Membrane Tension Indentation Engine study by ID."""
    repo = PiezoMechanosensitiveChannelGatingRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
