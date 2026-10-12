"""FastAPI routes for Phase 439: Autonomous Flagellar Motor Stochastic Switching & Bacterial Chemotaxis Run-Tumble Trajectory Simulator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.bacterial_chemotaxis_run_tumble_simulator_repo import BacterialChemotaxisSimulatorRepository
from research.orchestration.bacterial_chemotaxis_run_tumble_simulator_engine import BacterialChemotaxisSimulatorEngine

router = APIRouter(prefix="/bacterial-chemotaxis-simulator", tags=["bacterial-chemotaxis-simulator"])


class AnalyzeBacterialChemotaxisSimulatorRequest(BaseModel):
    name: str = Field(..., example="Autonomous Flagellar Motor Stochastic Switching & Bacterial Chemotaxis Run-Tumble Trajectory Simulator Run")
    target_specimen: str = Field(default="E. coli K-12 Motile Swarm in Microfluidic Attractant/Repellent Gradient")
    analytical_modality: str = Field(default="chemotaxis-run-tumble")
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


class BacterialChemotaxisSimulatorStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    run_duration_mean_seconds: float
    tumble_frequency_hz: float
    chemotactic_drift_velocity_um_per_s: float
    chey_p_phosphorylation_equilibrium: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=BacterialChemotaxisSimulatorStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_bacterial_chemotaxis_run_tumble_simulator(
    req: AnalyzeBacterialChemotaxisSimulatorRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Flagellar Motor Stochastic Switching & Bacterial Chemotaxis Run-Tumble Trajectory Simulator analysis and persist study."""
    engine = BacterialChemotaxisSimulatorEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = BacterialChemotaxisSimulatorRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        run_duration_mean_seconds=result.run_duration_mean_seconds,
        tumble_frequency_hz=result.tumble_frequency_hz,
        chemotactic_drift_velocity_um_per_s=result.chemotactic_drift_velocity_um_per_s,
        chey_p_phosphorylation_equilibrium=result.chey_p_phosphorylation_equilibrium,
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

    return BacterialChemotaxisSimulatorStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        run_duration_mean_seconds=study.run_duration_mean_seconds,
        tumble_frequency_hz=study.tumble_frequency_hz,
        chemotactic_drift_velocity_um_per_s=study.chemotactic_drift_velocity_um_per_s,
        chey_p_phosphorylation_equilibrium=study.chey_p_phosphorylation_equilibrium,
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


@router.get("/studies", response_model=List[BacterialChemotaxisSimulatorStudyResponse])
async def list_bacterial_chemotaxis_run_tumble_simulator_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Flagellar Motor Stochastic Switching & Bacterial Chemotaxis Run-Tumble Trajectory Simulator studies."""
    repo = BacterialChemotaxisSimulatorRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=BacterialChemotaxisSimulatorStudyResponse)
async def get_bacterial_chemotaxis_run_tumble_simulator_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Flagellar Motor Stochastic Switching & Bacterial Chemotaxis Run-Tumble Trajectory Simulator study by ID."""
    repo = BacterialChemotaxisSimulatorRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
