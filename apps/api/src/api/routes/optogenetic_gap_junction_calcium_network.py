"""FastAPI routes for Phase 554: Autonomous Optogenetic Intercellular Gap Junction Coupling & Calcium Synchrony Network Forecaster."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.optogenetic_gap_junction_calcium_network_repo import OptogeneticGapJunctionCalciumNetworkRepository
from research.orchestration.optogenetic_gap_junction_calcium_network_engine import OptogeneticGapJunctionCalciumNetworkEngine

router = APIRouter(prefix="/optogenetic-gap-junction-calcium-network", tags=["optogenetic-gap-junction-calcium-network"])


class AnalyzeOptogeneticGapJunctionCalciumNetworkRequest(BaseModel):
    name: str = Field(..., example="Autonomous Optogenetic Intercellular Gap Junction Coupling & Calcium Synchrony Network Forecaster Run")
    target_specimen: str = Field(default="Confluent Monolayer of Human Induced Pluripotent Stem Cell-Derived Cardiomyocytes expressing Channelrhodopsin-2 and Connexin-43")
    analytical_modality: str = Field(default="optogenetic-gap-junction-sync")
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


class OptogeneticGapJunctionCalciumNetworkStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    calcium_wave_propagation_velocity_um_s: float
    connexin43_gap_junction_conductance_ns: float
    network_phase_synchronization_order_param: float
    action_potential_duration_apd90_ms: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=OptogeneticGapJunctionCalciumNetworkStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_optogenetic_gap_junction_calcium_network(
    req: AnalyzeOptogeneticGapJunctionCalciumNetworkRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Optogenetic Intercellular Gap Junction Coupling & Calcium Synchrony Network Forecaster analysis and persist study."""
    engine = OptogeneticGapJunctionCalciumNetworkEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = OptogeneticGapJunctionCalciumNetworkRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        calcium_wave_propagation_velocity_um_s=result.calcium_wave_propagation_velocity_um_s,
        connexin43_gap_junction_conductance_ns=result.connexin43_gap_junction_conductance_ns,
        network_phase_synchronization_order_param=result.network_phase_synchronization_order_param,
        action_potential_duration_apd90_ms=result.action_potential_duration_apd90_ms,
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

    return OptogeneticGapJunctionCalciumNetworkStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        calcium_wave_propagation_velocity_um_s=study.calcium_wave_propagation_velocity_um_s,
        connexin43_gap_junction_conductance_ns=study.connexin43_gap_junction_conductance_ns,
        network_phase_synchronization_order_param=study.network_phase_synchronization_order_param,
        action_potential_duration_apd90_ms=study.action_potential_duration_apd90_ms,
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


@router.get("/studies", response_model=List[OptogeneticGapJunctionCalciumNetworkStudyResponse])
async def list_optogenetic_gap_junction_calcium_network_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Optogenetic Intercellular Gap Junction Coupling & Calcium Synchrony Network Forecaster studies."""
    repo = OptogeneticGapJunctionCalciumNetworkRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=OptogeneticGapJunctionCalciumNetworkStudyResponse)
async def get_optogenetic_gap_junction_calcium_network_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Optogenetic Intercellular Gap Junction Coupling & Calcium Synchrony Network Forecaster study by ID."""
    repo = OptogeneticGapJunctionCalciumNetworkRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
