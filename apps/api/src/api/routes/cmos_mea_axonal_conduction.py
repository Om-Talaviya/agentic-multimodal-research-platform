"""FastAPI routes for Phase 490: Autonomous High-Density CMOS Microelectrode Array Neuromorphic Axonal Conduction Velocity Mapper."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.cmos_mea_axonal_conduction_repo import CmosMeaAxonalConductionRepository
from research.orchestration.cmos_mea_axonal_conduction_engine import CmosMeaAxonalConductionEngine

router = APIRouter(prefix="/cmos-mea-axonal-conduction", tags=["cmos-mea-axonal-conduction"])


class AnalyzeCmosMeaAxonalConductionRequest(BaseModel):
    name: str = Field(..., example="Autonomous High-Density CMOS Microelectrode Array Neuromorphic Axonal Conduction Velocity Mapper Run")
    target_specimen: str = Field(default="Rat Cortical Primary Neurons Cultured over 26,400 Platinum Electrode CMOS Biocompatible Chip")
    analytical_modality: str = Field(default="cmos-mea-axonal-conduction")
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


class CmosMeaAxonalConductionStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    axonal_action_potential_conduction_velocity_m_per_s: float
    spike_signal_to_noise_ratio_snr: float
    synaptic_propagation_latency_ms: float
    functional_synaptic_connectivity_density: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=CmosMeaAxonalConductionStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_cmos_mea_axonal_conduction(
    req: AnalyzeCmosMeaAxonalConductionRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous High-Density CMOS Microelectrode Array Neuromorphic Axonal Conduction Velocity Mapper analysis and persist study."""
    engine = CmosMeaAxonalConductionEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = CmosMeaAxonalConductionRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        axonal_action_potential_conduction_velocity_m_per_s=result.axonal_action_potential_conduction_velocity_m_per_s,
        spike_signal_to_noise_ratio_snr=result.spike_signal_to_noise_ratio_snr,
        synaptic_propagation_latency_ms=result.synaptic_propagation_latency_ms,
        functional_synaptic_connectivity_density=result.functional_synaptic_connectivity_density,
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

    return CmosMeaAxonalConductionStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        axonal_action_potential_conduction_velocity_m_per_s=study.axonal_action_potential_conduction_velocity_m_per_s,
        spike_signal_to_noise_ratio_snr=study.spike_signal_to_noise_ratio_snr,
        synaptic_propagation_latency_ms=study.synaptic_propagation_latency_ms,
        functional_synaptic_connectivity_density=study.functional_synaptic_connectivity_density,
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


@router.get("/studies", response_model=List[CmosMeaAxonalConductionStudyResponse])
async def list_cmos_mea_axonal_conduction_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous High-Density CMOS Microelectrode Array Neuromorphic Axonal Conduction Velocity Mapper studies."""
    repo = CmosMeaAxonalConductionRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=CmosMeaAxonalConductionStudyResponse)
async def get_cmos_mea_axonal_conduction_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous High-Density CMOS Microelectrode Array Neuromorphic Axonal Conduction Velocity Mapper study by ID."""
    repo = CmosMeaAxonalConductionRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
