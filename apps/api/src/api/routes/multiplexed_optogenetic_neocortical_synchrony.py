"""FastAPI routes for Phase 517: Autonomous Dual-Color Multiplexed Optogenetic Neocortical Oscillatory Synchrony Mapper."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.multiplexed_optogenetic_neocortical_synchrony_repo import MultiplexedOptogeneticNeocorticalSynchronyRepository
from research.orchestration.multiplexed_optogenetic_neocortical_synchrony_engine import MultiplexedOptogeneticNeocorticalSynchronyEngine

router = APIRouter(prefix="/multiplexed-optogenetic-neocortical-synchrony", tags=["multiplexed-optogenetic-neocortical-synchrony"])


class AnalyzeMultiplexedOptogeneticNeocorticalSynchronyRequest(BaseModel):
    name: str = Field(..., example="Autonomous Dual-Color Multiplexed Optogenetic Neocortical Oscillatory Synchrony Mapper Run")
    target_specimen: str = Field(default="Transgenic Mouse Somatosensory Cortex expressing ChRmine (Red) and ChETA (Blue) in Layer 2/3 and 5")
    analytical_modality: str = Field(default="dual-color-optogenetic-synchrony")
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


class MultiplexedOptogeneticNeocorticalSynchronyStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    gamma_band_phase_locking_value_plv: float
    optical_crosstalk_attenuation_ratio: float
    spike_timing_jitter_precision_std_ms: float
    cross_layer_laminar_information_transfer_entropy: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=MultiplexedOptogeneticNeocorticalSynchronyStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_multiplexed_optogenetic_neocortical_synchrony(
    req: AnalyzeMultiplexedOptogeneticNeocorticalSynchronyRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Dual-Color Multiplexed Optogenetic Neocortical Oscillatory Synchrony Mapper analysis and persist study."""
    engine = MultiplexedOptogeneticNeocorticalSynchronyEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = MultiplexedOptogeneticNeocorticalSynchronyRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        gamma_band_phase_locking_value_plv=result.gamma_band_phase_locking_value_plv,
        optical_crosstalk_attenuation_ratio=result.optical_crosstalk_attenuation_ratio,
        spike_timing_jitter_precision_std_ms=result.spike_timing_jitter_precision_std_ms,
        cross_layer_laminar_information_transfer_entropy=result.cross_layer_laminar_information_transfer_entropy,
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

    return MultiplexedOptogeneticNeocorticalSynchronyStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        gamma_band_phase_locking_value_plv=study.gamma_band_phase_locking_value_plv,
        optical_crosstalk_attenuation_ratio=study.optical_crosstalk_attenuation_ratio,
        spike_timing_jitter_precision_std_ms=study.spike_timing_jitter_precision_std_ms,
        cross_layer_laminar_information_transfer_entropy=study.cross_layer_laminar_information_transfer_entropy,
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


@router.get("/studies", response_model=List[MultiplexedOptogeneticNeocorticalSynchronyStudyResponse])
async def list_multiplexed_optogenetic_neocortical_synchrony_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Dual-Color Multiplexed Optogenetic Neocortical Oscillatory Synchrony Mapper studies."""
    repo = MultiplexedOptogeneticNeocorticalSynchronyRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=MultiplexedOptogeneticNeocorticalSynchronyStudyResponse)
async def get_multiplexed_optogenetic_neocortical_synchrony_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Dual-Color Multiplexed Optogenetic Neocortical Oscillatory Synchrony Mapper study by ID."""
    repo = MultiplexedOptogeneticNeocorticalSynchronyRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
