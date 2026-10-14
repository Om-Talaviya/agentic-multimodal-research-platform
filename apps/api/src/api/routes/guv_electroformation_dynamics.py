"""FastAPI routes for Phase 480: Autonomous Synthetic Protocellular Giant Unilamellar Vesicle (GUV) Electroformation Simulator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.guv_electroformation_dynamics_repo import GuvElectroformationDynamicsRepository
from research.orchestration.guv_electroformation_dynamics_engine import GuvElectroformationDynamicsEngine

router = APIRouter(prefix="/guv-electroformation-dynamics", tags=["guv-electroformation-dynamics"])


class AnalyzeGuvElectroformationDynamicsRequest(BaseModel):
    name: str = Field(..., example="Autonomous Synthetic Protocellular Giant Unilamellar Vesicle (GUV) Electroformation Simulator Run")
    target_specimen: str = Field(default="Indium Tin Oxide (ITO) Microelectrode Chamber with POPC/Cholesterol Bilayer Hydration")
    analytical_modality: str = Field(default="guv-electroformation-dynamics")
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


class GuvElectroformationDynamicsStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    guv_mean_diameter_yield_um: float
    bilayer_bending_rigidity_kbT: float
    electric_field_interfacial_shear_V_per_m: float
    unilamellarity_monodispersity_cv: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=GuvElectroformationDynamicsStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_guv_electroformation_dynamics(
    req: AnalyzeGuvElectroformationDynamicsRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Synthetic Protocellular Giant Unilamellar Vesicle (GUV) Electroformation Simulator analysis and persist study."""
    engine = GuvElectroformationDynamicsEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = GuvElectroformationDynamicsRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        guv_mean_diameter_yield_um=result.guv_mean_diameter_yield_um,
        bilayer_bending_rigidity_kbT=result.bilayer_bending_rigidity_kbT,
        electric_field_interfacial_shear_V_per_m=result.electric_field_interfacial_shear_V_per_m,
        unilamellarity_monodispersity_cv=result.unilamellarity_monodispersity_cv,
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

    return GuvElectroformationDynamicsStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        guv_mean_diameter_yield_um=study.guv_mean_diameter_yield_um,
        bilayer_bending_rigidity_kbT=study.bilayer_bending_rigidity_kbT,
        electric_field_interfacial_shear_V_per_m=study.electric_field_interfacial_shear_V_per_m,
        unilamellarity_monodispersity_cv=study.unilamellarity_monodispersity_cv,
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


@router.get("/studies", response_model=List[GuvElectroformationDynamicsStudyResponse])
async def list_guv_electroformation_dynamics_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Synthetic Protocellular Giant Unilamellar Vesicle (GUV) Electroformation Simulator studies."""
    repo = GuvElectroformationDynamicsRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=GuvElectroformationDynamicsStudyResponse)
async def get_guv_electroformation_dynamics_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Synthetic Protocellular Giant Unilamellar Vesicle (GUV) Electroformation Simulator study by ID."""
    repo = GuvElectroformationDynamicsRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
