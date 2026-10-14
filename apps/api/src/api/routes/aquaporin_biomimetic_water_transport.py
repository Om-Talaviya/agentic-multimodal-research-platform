"""FastAPI routes for Phase 491: Autonomous Biomimetic Synthetic Membrane Water Aquaporin Channel Transport Forecaster."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.aquaporin_biomimetic_water_transport_repo import AquaporinBiomimeticWaterTransportRepository
from research.orchestration.aquaporin_biomimetic_water_transport_engine import AquaporinBiomimeticWaterTransportEngine

router = APIRouter(prefix="/aquaporin-biomimetic-water-transport", tags=["aquaporin-biomimetic-water-transport"])


class AnalyzeAquaporinBiomimeticWaterTransportRequest(BaseModel):
    name: str = Field(..., example="Autonomous Biomimetic Synthetic Membrane Water Aquaporin Channel Transport Forecaster Run")
    target_specimen: str = Field(default="Polymer-Inorganic Biomimetic Aquaporin-Z Nanocomposite Membrane with Forward Osmosis Crossflow")
    analytical_modality: str = Field(default="aquaporin-biomimetic-transport")
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


class AquaporinBiomimeticWaterTransportStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    water_permeability_flux_lmh_bar: float
    nacl_solute_rejection_percentage: float
    aquaporin_channel_incorporation_density_per_um2: float
    single_pore_osmotic_permeability_pf_cm3_per_s: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=AquaporinBiomimeticWaterTransportStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_aquaporin_biomimetic_water_transport(
    req: AnalyzeAquaporinBiomimeticWaterTransportRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Biomimetic Synthetic Membrane Water Aquaporin Channel Transport Forecaster analysis and persist study."""
    engine = AquaporinBiomimeticWaterTransportEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = AquaporinBiomimeticWaterTransportRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        water_permeability_flux_lmh_bar=result.water_permeability_flux_lmh_bar,
        nacl_solute_rejection_percentage=result.nacl_solute_rejection_percentage,
        aquaporin_channel_incorporation_density_per_um2=result.aquaporin_channel_incorporation_density_per_um2,
        single_pore_osmotic_permeability_pf_cm3_per_s=result.single_pore_osmotic_permeability_pf_cm3_per_s,
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

    return AquaporinBiomimeticWaterTransportStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        water_permeability_flux_lmh_bar=study.water_permeability_flux_lmh_bar,
        nacl_solute_rejection_percentage=study.nacl_solute_rejection_percentage,
        aquaporin_channel_incorporation_density_per_um2=study.aquaporin_channel_incorporation_density_per_um2,
        single_pore_osmotic_permeability_pf_cm3_per_s=study.single_pore_osmotic_permeability_pf_cm3_per_s,
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


@router.get("/studies", response_model=List[AquaporinBiomimeticWaterTransportStudyResponse])
async def list_aquaporin_biomimetic_water_transport_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Biomimetic Synthetic Membrane Water Aquaporin Channel Transport Forecaster studies."""
    repo = AquaporinBiomimeticWaterTransportRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=AquaporinBiomimeticWaterTransportStudyResponse)
async def get_aquaporin_biomimetic_water_transport_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Biomimetic Synthetic Membrane Water Aquaporin Channel Transport Forecaster study by ID."""
    repo = AquaporinBiomimeticWaterTransportRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
