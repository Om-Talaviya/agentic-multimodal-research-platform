"""FastAPI routes for Phase 519: Autonomous Non-Equilibrium Active Matter Cytoskeletal Topological Defect Self-Propulsion Simulator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.active_matter_cytoskeletal_nematic_defect_repo import ActiveMatterCytoskeletalNematicDefectRepository
from research.orchestration.active_matter_cytoskeletal_nematic_defect_engine import ActiveMatterCytoskeletalNematicDefectEngine

router = APIRouter(prefix="/active-matter-cytoskeletal-nematic-defect", tags=["active-matter-cytoskeletal-nematic-defect"])


class AnalyzeActiveMatterCytoskeletalNematicDefectRequest(BaseModel):
    name: str = Field(..., example="Autonomous Non-Equilibrium Active Matter Cytoskeletal Topological Defect Self-Propulsion Simulator Run")
    target_specimen: str = Field(default="Microtubule-Kinesin Active Gel Nematic Liquid Crystal Layer at Oil-Water Interface")
    analytical_modality: str = Field(default="active-nematic-matter-dynamics")
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


class ActiveMatterCytoskeletalNematicDefectStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    topological_defect_annihilation_rate_s_inv: float
    active_turbulent_vortex_correlation_length_um: float
    plus_half_defect_self_propulsion_velocity_um_per_s: float
    atp_fuel_hydrolysis_energy_dissipation_rate_W_per_m3: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=ActiveMatterCytoskeletalNematicDefectStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_active_matter_cytoskeletal_nematic_defect(
    req: AnalyzeActiveMatterCytoskeletalNematicDefectRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Non-Equilibrium Active Matter Cytoskeletal Topological Defect Self-Propulsion Simulator analysis and persist study."""
    engine = ActiveMatterCytoskeletalNematicDefectEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = ActiveMatterCytoskeletalNematicDefectRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        topological_defect_annihilation_rate_s_inv=result.topological_defect_annihilation_rate_s_inv,
        active_turbulent_vortex_correlation_length_um=result.active_turbulent_vortex_correlation_length_um,
        plus_half_defect_self_propulsion_velocity_um_per_s=result.plus_half_defect_self_propulsion_velocity_um_per_s,
        atp_fuel_hydrolysis_energy_dissipation_rate_W_per_m3=result.atp_fuel_hydrolysis_energy_dissipation_rate_W_per_m3,
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

    return ActiveMatterCytoskeletalNematicDefectStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        topological_defect_annihilation_rate_s_inv=study.topological_defect_annihilation_rate_s_inv,
        active_turbulent_vortex_correlation_length_um=study.active_turbulent_vortex_correlation_length_um,
        plus_half_defect_self_propulsion_velocity_um_per_s=study.plus_half_defect_self_propulsion_velocity_um_per_s,
        atp_fuel_hydrolysis_energy_dissipation_rate_W_per_m3=study.atp_fuel_hydrolysis_energy_dissipation_rate_W_per_m3,
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


@router.get("/studies", response_model=List[ActiveMatterCytoskeletalNematicDefectStudyResponse])
async def list_active_matter_cytoskeletal_nematic_defect_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Non-Equilibrium Active Matter Cytoskeletal Topological Defect Self-Propulsion Simulator studies."""
    repo = ActiveMatterCytoskeletalNematicDefectRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=ActiveMatterCytoskeletalNematicDefectStudyResponse)
async def get_active_matter_cytoskeletal_nematic_defect_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Non-Equilibrium Active Matter Cytoskeletal Topological Defect Self-Propulsion Simulator study by ID."""
    repo = ActiveMatterCytoskeletalNematicDefectRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
