"""FastAPI routes for Phase 500: Autonomous Bioelectronic Living Biomaterial Microbial Electron Transport Network Modeler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.bioelectronic_living_materials_network_repo import BioelectronicLivingMaterialsNetworkRepository
from research.orchestration.bioelectronic_living_materials_network_engine import BioelectronicLivingMaterialsNetworkEngine

router = APIRouter(prefix="/bioelectronic-living-materials-network", tags=["bioelectronic-living-materials-network"])


class AnalyzeBioelectronicLivingMaterialsNetworkRequest(BaseModel):
    name: str = Field(..., example="Autonomous Bioelectronic Living Biomaterial Microbial Electron Transport Network Modeler Run")
    target_specimen: str = Field(default="Geobacter sulfurreducens Engineered Electrically Conductive Cytochrome Pili Hydrogel Matrix")
    analytical_modality: str = Field(default="bioelectronic-living-materials")
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


class BioelectronicLivingMaterialsNetworkStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    matrix_electrical_conductivity_S_per_cm: float
    redox_cytochrome_hopping_rate_s_inv: float
    current_density_production_mA_per_cm2: float
    longitudinal_charge_transfer_efficiency: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=BioelectronicLivingMaterialsNetworkStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_bioelectronic_living_materials_network(
    req: AnalyzeBioelectronicLivingMaterialsNetworkRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Bioelectronic Living Biomaterial Microbial Electron Transport Network Modeler analysis and persist study."""
    engine = BioelectronicLivingMaterialsNetworkEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = BioelectronicLivingMaterialsNetworkRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        matrix_electrical_conductivity_S_per_cm=result.matrix_electrical_conductivity_S_per_cm,
        redox_cytochrome_hopping_rate_s_inv=result.redox_cytochrome_hopping_rate_s_inv,
        current_density_production_mA_per_cm2=result.current_density_production_mA_per_cm2,
        longitudinal_charge_transfer_efficiency=result.longitudinal_charge_transfer_efficiency,
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

    return BioelectronicLivingMaterialsNetworkStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        matrix_electrical_conductivity_S_per_cm=study.matrix_electrical_conductivity_S_per_cm,
        redox_cytochrome_hopping_rate_s_inv=study.redox_cytochrome_hopping_rate_s_inv,
        current_density_production_mA_per_cm2=study.current_density_production_mA_per_cm2,
        longitudinal_charge_transfer_efficiency=study.longitudinal_charge_transfer_efficiency,
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


@router.get("/studies", response_model=List[BioelectronicLivingMaterialsNetworkStudyResponse])
async def list_bioelectronic_living_materials_network_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Bioelectronic Living Biomaterial Microbial Electron Transport Network Modeler studies."""
    repo = BioelectronicLivingMaterialsNetworkRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=BioelectronicLivingMaterialsNetworkStudyResponse)
async def get_bioelectronic_living_materials_network_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Bioelectronic Living Biomaterial Microbial Electron Transport Network Modeler study by ID."""
    repo = BioelectronicLivingMaterialsNetworkRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
