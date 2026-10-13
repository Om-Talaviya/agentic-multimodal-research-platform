"""FastAPI routes for Phase 453: Autonomous Quantum Dots-Mediated Optoelectronic Neuromorphic Synaptic Potentiation Modeler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.quantum_dots_optoelectronic_synapse_repo import QuantumDotsOptoelectronicSynapseRepository
from research.orchestration.quantum_dots_optoelectronic_synapse_engine import QuantumDotsOptoelectronicSynapseEngine

router = APIRouter(prefix="/quantum-dots-optoelectronic-synapse", tags=["quantum-dots-optoelectronic-synapse"])


class AnalyzeQuantumDotsOptoelectronicSynapseRequest(BaseModel):
    name: str = Field(..., example="Autonomous Quantum Dots-Mediated Optoelectronic Neuromorphic Synaptic Potentiation Modeler Run")
    target_specimen: str = Field(default="InP/ZnS Core-Shell Quantum Dot Photo-Memristor Synapse Coupled to Primary Cortical Neurons")
    analytical_modality: str = Field(default="qd-optoelectronic-synapse")
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


class QuantumDotsOptoelectronicSynapseStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    paired_pulse_facilitation_ppf_ratio: float
    photocurrent_relaxation_lifetime_ms: float
    synaptic_weight_plasticity_dynamic_range: float
    energy_consumption_per_spike_femtojoules: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=QuantumDotsOptoelectronicSynapseStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_quantum_dots_optoelectronic_synapse(
    req: AnalyzeQuantumDotsOptoelectronicSynapseRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Quantum Dots-Mediated Optoelectronic Neuromorphic Synaptic Potentiation Modeler analysis and persist study."""
    engine = QuantumDotsOptoelectronicSynapseEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = QuantumDotsOptoelectronicSynapseRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        paired_pulse_facilitation_ppf_ratio=result.paired_pulse_facilitation_ppf_ratio,
        photocurrent_relaxation_lifetime_ms=result.photocurrent_relaxation_lifetime_ms,
        synaptic_weight_plasticity_dynamic_range=result.synaptic_weight_plasticity_dynamic_range,
        energy_consumption_per_spike_femtojoules=result.energy_consumption_per_spike_femtojoules,
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

    return QuantumDotsOptoelectronicSynapseStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        paired_pulse_facilitation_ppf_ratio=study.paired_pulse_facilitation_ppf_ratio,
        photocurrent_relaxation_lifetime_ms=study.photocurrent_relaxation_lifetime_ms,
        synaptic_weight_plasticity_dynamic_range=study.synaptic_weight_plasticity_dynamic_range,
        energy_consumption_per_spike_femtojoules=study.energy_consumption_per_spike_femtojoules,
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


@router.get("/studies", response_model=List[QuantumDotsOptoelectronicSynapseStudyResponse])
async def list_quantum_dots_optoelectronic_synapse_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Quantum Dots-Mediated Optoelectronic Neuromorphic Synaptic Potentiation Modeler studies."""
    repo = QuantumDotsOptoelectronicSynapseRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=QuantumDotsOptoelectronicSynapseStudyResponse)
async def get_quantum_dots_optoelectronic_synapse_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Quantum Dots-Mediated Optoelectronic Neuromorphic Synaptic Potentiation Modeler study by ID."""
    repo = QuantumDotsOptoelectronicSynapseRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
