"""FastAPI routes for Phase 543: Autonomous Biomimetic Neuromorphic Optoelectronic Synapse Photo-Memristive Plasticity Forecaster."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.neuromorphic_optogenetic_synaptic_emulator_repo import NeuromorphicOptogeneticSynapticEmulatorRepository
from research.orchestration.neuromorphic_optogenetic_synaptic_emulator_engine import NeuromorphicOptogeneticSynapticEmulatorEngine

router = APIRouter(prefix="/neuromorphic-optogenetic-synaptic-emulator", tags=["neuromorphic-optogenetic-synaptic-emulator"])


class AnalyzeNeuromorphicOptogeneticSynapticEmulatorRequest(BaseModel):
    name: str = Field(..., example="Autonomous Biomimetic Neuromorphic Optoelectronic Synapse Photo-Memristive Plasticity Forecaster Run")
    target_specimen: str = Field(default="2D Transition Metal Dichalcogenide (MoS2) / Perovskite Heterostructure Optoelectronic Synaptic Memristor")
    analytical_modality: str = Field(default="optoelectronic-synapse-plasticity")
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


class NeuromorphicOptogeneticSynapticEmulatorStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    paired_pulse_facilitation_ppf_index_pct: float
    photo_induced_potentiation_energy_per_spike_fj: float
    non_volatile_memory_retention_days: float
    linear_weight_update_dynamic_range: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=NeuromorphicOptogeneticSynapticEmulatorStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_neuromorphic_optogenetic_synaptic_emulator(
    req: AnalyzeNeuromorphicOptogeneticSynapticEmulatorRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Biomimetic Neuromorphic Optoelectronic Synapse Photo-Memristive Plasticity Forecaster analysis and persist study."""
    engine = NeuromorphicOptogeneticSynapticEmulatorEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = NeuromorphicOptogeneticSynapticEmulatorRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        paired_pulse_facilitation_ppf_index_pct=result.paired_pulse_facilitation_ppf_index_pct,
        photo_induced_potentiation_energy_per_spike_fj=result.photo_induced_potentiation_energy_per_spike_fj,
        non_volatile_memory_retention_days=result.non_volatile_memory_retention_days,
        linear_weight_update_dynamic_range=result.linear_weight_update_dynamic_range,
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

    return NeuromorphicOptogeneticSynapticEmulatorStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        paired_pulse_facilitation_ppf_index_pct=study.paired_pulse_facilitation_ppf_index_pct,
        photo_induced_potentiation_energy_per_spike_fj=study.photo_induced_potentiation_energy_per_spike_fj,
        non_volatile_memory_retention_days=study.non_volatile_memory_retention_days,
        linear_weight_update_dynamic_range=study.linear_weight_update_dynamic_range,
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


@router.get("/studies", response_model=List[NeuromorphicOptogeneticSynapticEmulatorStudyResponse])
async def list_neuromorphic_optogenetic_synaptic_emulator_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Biomimetic Neuromorphic Optoelectronic Synapse Photo-Memristive Plasticity Forecaster studies."""
    repo = NeuromorphicOptogeneticSynapticEmulatorRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=NeuromorphicOptogeneticSynapticEmulatorStudyResponse)
async def get_neuromorphic_optogenetic_synaptic_emulator_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Biomimetic Neuromorphic Optoelectronic Synapse Photo-Memristive Plasticity Forecaster study by ID."""
    repo = NeuromorphicOptogeneticSynapticEmulatorRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
