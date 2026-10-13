"""FastAPI routes for Phase 466: Autonomous Optogenetic Rheotaxis Bacterial Micro-Swarm Bio-Convective Flow Modeler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.optogenetic_rheotaxis_micro_swarm_repo import OptogeneticRheotaxisMicroSwarmRepository
from research.orchestration.optogenetic_rheotaxis_micro_swarm_engine import OptogeneticRheotaxisMicroSwarmEngine

router = APIRouter(prefix="/optogenetic-rheotaxis-micro-swarm", tags=["optogenetic-rheotaxis-micro-swarm"])


class AnalyzeOptogeneticRheotaxisMicroSwarmRequest(BaseModel):
    name: str = Field(..., example="Autonomous Optogenetic Rheotaxis Bacterial Micro-Swarm Bio-Convective Flow Modeler Run")
    target_specimen: str = Field(default="Engineered B. subtilis Swarm with Light-Gated Flagellar Torque Switch in Laminar Microfluidic Channel")
    analytical_modality: str = Field(default="optogenetic-rheotaxis-swarm")
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


class OptogeneticRheotaxisMicroSwarmStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    micro_swarm_upstream_drift_velocity_um_s: float
    bioconvective_plume_wavelength_um: float
    light_stimulated_phototactic_bias_ratio: float
    vorticity_enstrophy_metric: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=OptogeneticRheotaxisMicroSwarmStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_optogenetic_rheotaxis_micro_swarm(
    req: AnalyzeOptogeneticRheotaxisMicroSwarmRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Optogenetic Rheotaxis Bacterial Micro-Swarm Bio-Convective Flow Modeler analysis and persist study."""
    engine = OptogeneticRheotaxisMicroSwarmEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = OptogeneticRheotaxisMicroSwarmRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        micro_swarm_upstream_drift_velocity_um_s=result.micro_swarm_upstream_drift_velocity_um_s,
        bioconvective_plume_wavelength_um=result.bioconvective_plume_wavelength_um,
        light_stimulated_phototactic_bias_ratio=result.light_stimulated_phototactic_bias_ratio,
        vorticity_enstrophy_metric=result.vorticity_enstrophy_metric,
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

    return OptogeneticRheotaxisMicroSwarmStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        micro_swarm_upstream_drift_velocity_um_s=study.micro_swarm_upstream_drift_velocity_um_s,
        bioconvective_plume_wavelength_um=study.bioconvective_plume_wavelength_um,
        light_stimulated_phototactic_bias_ratio=study.light_stimulated_phototactic_bias_ratio,
        vorticity_enstrophy_metric=study.vorticity_enstrophy_metric,
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


@router.get("/studies", response_model=List[OptogeneticRheotaxisMicroSwarmStudyResponse])
async def list_optogenetic_rheotaxis_micro_swarm_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Optogenetic Rheotaxis Bacterial Micro-Swarm Bio-Convective Flow Modeler studies."""
    repo = OptogeneticRheotaxisMicroSwarmRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=OptogeneticRheotaxisMicroSwarmStudyResponse)
async def get_optogenetic_rheotaxis_micro_swarm_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Optogenetic Rheotaxis Bacterial Micro-Swarm Bio-Convective Flow Modeler study by ID."""
    repo = OptogeneticRheotaxisMicroSwarmRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
