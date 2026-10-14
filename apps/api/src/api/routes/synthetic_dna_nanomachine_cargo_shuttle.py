"""FastAPI routes for Phase 523: Autonomous Autonomous DNA Nanomachine Cargo Transport Track Walker & Dynamic Shuttle."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.synthetic_dna_nanomachine_cargo_shuttle_repo import SyntheticDnaNanomachineCargoShuttleRepository
from research.orchestration.synthetic_dna_nanomachine_cargo_shuttle_engine import SyntheticDnaNanomachineCargoShuttleEngine

router = APIRouter(prefix="/synthetic-dna-nanomachine-cargo-shuttle", tags=["synthetic-dna-nanomachine-cargo-shuttle"])


class AnalyzeSyntheticDnaNanomachineCargoShuttleRequest(BaseModel):
    name: str = Field(..., example="Autonomous Autonomous DNA Nanomachine Cargo Transport Track Walker & Dynamic Shuttle Run")
    target_specimen: str = Field(default="Scaffolded DNA Origami 2D Origami Track with Autonomous Kinesin-Mimic Fuel-Fueled DNA Bipedal Walker")
    analytical_modality: str = Field(default="dna-nanomachine-shuttle")
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


class SyntheticDnaNanomachineCargoShuttleStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    walker_directional_velocity_nm_per_min: float
    fuel_strand_consumption_efficiency: float
    molecular_cargo_handover_fidelity_pct: float
    continuous_processive_stepping_distance_nm: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=SyntheticDnaNanomachineCargoShuttleStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_synthetic_dna_nanomachine_cargo_shuttle(
    req: AnalyzeSyntheticDnaNanomachineCargoShuttleRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Autonomous DNA Nanomachine Cargo Transport Track Walker & Dynamic Shuttle analysis and persist study."""
    engine = SyntheticDnaNanomachineCargoShuttleEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SyntheticDnaNanomachineCargoShuttleRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        walker_directional_velocity_nm_per_min=result.walker_directional_velocity_nm_per_min,
        fuel_strand_consumption_efficiency=result.fuel_strand_consumption_efficiency,
        molecular_cargo_handover_fidelity_pct=result.molecular_cargo_handover_fidelity_pct,
        continuous_processive_stepping_distance_nm=result.continuous_processive_stepping_distance_nm,
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

    return SyntheticDnaNanomachineCargoShuttleStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        walker_directional_velocity_nm_per_min=study.walker_directional_velocity_nm_per_min,
        fuel_strand_consumption_efficiency=study.fuel_strand_consumption_efficiency,
        molecular_cargo_handover_fidelity_pct=study.molecular_cargo_handover_fidelity_pct,
        continuous_processive_stepping_distance_nm=study.continuous_processive_stepping_distance_nm,
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


@router.get("/studies", response_model=List[SyntheticDnaNanomachineCargoShuttleStudyResponse])
async def list_synthetic_dna_nanomachine_cargo_shuttle_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Autonomous DNA Nanomachine Cargo Transport Track Walker & Dynamic Shuttle studies."""
    repo = SyntheticDnaNanomachineCargoShuttleRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SyntheticDnaNanomachineCargoShuttleStudyResponse)
async def get_synthetic_dna_nanomachine_cargo_shuttle_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Autonomous DNA Nanomachine Cargo Transport Track Walker & Dynamic Shuttle study by ID."""
    repo = SyntheticDnaNanomachineCargoShuttleRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
