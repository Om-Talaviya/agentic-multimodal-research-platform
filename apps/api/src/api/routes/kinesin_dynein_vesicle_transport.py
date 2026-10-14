"""FastAPI routes for Phase 474: Autonomous Subcellular Microtubule Kinesin-Dynein Tug-of-War Vesicle Transport Modeler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.kinesin_dynein_vesicle_transport_repo import KinesinDyneinVesicleTransportRepository
from research.orchestration.kinesin_dynein_vesicle_transport_engine import KinesinDyneinVesicleTransportEngine

router = APIRouter(prefix="/kinesin-dynein-vesicle-transport", tags=["kinesin-dynein-vesicle-transport"])


class AnalyzeKinesinDyneinVesicleTransportRequest(BaseModel):
    name: str = Field(..., example="Autonomous Subcellular Microtubule Kinesin-Dynein Tug-of-War Vesicle Transport Modeler Run")
    target_specimen: str = Field(default="Vitrified Axonal Microtubule Filament with Dual Kinesin-1 and Cytoplasmic Dynein Vesicle Cargo")
    analytical_modality: str = Field(default="kinesin-dynein-tug-of-war")
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


class KinesinDyneinVesicleTransportStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    anterograde_retrograde_velocity_ratio: float
    motor_detachment_stall_force_pN: float
    mean_run_length_processivity_um: float
    tug_of_war_cooperative_coordination_index: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=KinesinDyneinVesicleTransportStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_kinesin_dynein_vesicle_transport(
    req: AnalyzeKinesinDyneinVesicleTransportRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Subcellular Microtubule Kinesin-Dynein Tug-of-War Vesicle Transport Modeler analysis and persist study."""
    engine = KinesinDyneinVesicleTransportEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = KinesinDyneinVesicleTransportRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        anterograde_retrograde_velocity_ratio=result.anterograde_retrograde_velocity_ratio,
        motor_detachment_stall_force_pN=result.motor_detachment_stall_force_pN,
        mean_run_length_processivity_um=result.mean_run_length_processivity_um,
        tug_of_war_cooperative_coordination_index=result.tug_of_war_cooperative_coordination_index,
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

    return KinesinDyneinVesicleTransportStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        anterograde_retrograde_velocity_ratio=study.anterograde_retrograde_velocity_ratio,
        motor_detachment_stall_force_pN=study.motor_detachment_stall_force_pN,
        mean_run_length_processivity_um=study.mean_run_length_processivity_um,
        tug_of_war_cooperative_coordination_index=study.tug_of_war_cooperative_coordination_index,
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


@router.get("/studies", response_model=List[KinesinDyneinVesicleTransportStudyResponse])
async def list_kinesin_dynein_vesicle_transport_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Subcellular Microtubule Kinesin-Dynein Tug-of-War Vesicle Transport Modeler studies."""
    repo = KinesinDyneinVesicleTransportRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=KinesinDyneinVesicleTransportStudyResponse)
async def get_kinesin_dynein_vesicle_transport_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Subcellular Microtubule Kinesin-Dynein Tug-of-War Vesicle Transport Modeler study by ID."""
    repo = KinesinDyneinVesicleTransportRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
