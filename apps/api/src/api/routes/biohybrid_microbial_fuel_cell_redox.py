"""FastAPI routes for Phase 559: Autonomous Biohybrid Microbial Fuel Cell Extracellular Electron Shuttle Redox Kinetics Simulator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.biohybrid_microbial_fuel_cell_redox_repo import BiohybridMicrobialFuelCellRedoxRepository
from research.orchestration.biohybrid_microbial_fuel_cell_redox_engine import BiohybridMicrobialFuelCellRedoxEngine

router = APIRouter(prefix="/biohybrid-microbial-fuel-cell-redox", tags=["biohybrid-microbial-fuel-cell-redox"])


class AnalyzeBiohybridMicrobialFuelCellRedoxRequest(BaseModel):
    name: str = Field(..., example="Autonomous Biohybrid Microbial Fuel Cell Extracellular Electron Shuttle Redox Kinetics Simulator Run")
    target_specimen: str = Field(default="Shewanella oneidensis MR-1 living Biofilm grown on 3D Carbon Nanotube Anode with Riboflavin Redox Mediators")
    analytical_modality: str = Field(default="biohybrid-microbial-fuel-cell")
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


class BiohybridMicrobialFuelCellRedoxStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    anodic_current_density_ma_cm2: float
    extracellular_electron_transfer_rate_per_sec: float
    cytochrome_mtrc_reduction_potential_mv: float
    fuel_cell_maximum_power_density_mw_m2: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=BiohybridMicrobialFuelCellRedoxStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_biohybrid_microbial_fuel_cell_redox(
    req: AnalyzeBiohybridMicrobialFuelCellRedoxRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Biohybrid Microbial Fuel Cell Extracellular Electron Shuttle Redox Kinetics Simulator analysis and persist study."""
    engine = BiohybridMicrobialFuelCellRedoxEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = BiohybridMicrobialFuelCellRedoxRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        anodic_current_density_ma_cm2=result.anodic_current_density_ma_cm2,
        extracellular_electron_transfer_rate_per_sec=result.extracellular_electron_transfer_rate_per_sec,
        cytochrome_mtrc_reduction_potential_mv=result.cytochrome_mtrc_reduction_potential_mv,
        fuel_cell_maximum_power_density_mw_m2=result.fuel_cell_maximum_power_density_mw_m2,
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

    return BiohybridMicrobialFuelCellRedoxStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        anodic_current_density_ma_cm2=study.anodic_current_density_ma_cm2,
        extracellular_electron_transfer_rate_per_sec=study.extracellular_electron_transfer_rate_per_sec,
        cytochrome_mtrc_reduction_potential_mv=study.cytochrome_mtrc_reduction_potential_mv,
        fuel_cell_maximum_power_density_mw_m2=study.fuel_cell_maximum_power_density_mw_m2,
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


@router.get("/studies", response_model=List[BiohybridMicrobialFuelCellRedoxStudyResponse])
async def list_biohybrid_microbial_fuel_cell_redox_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Biohybrid Microbial Fuel Cell Extracellular Electron Shuttle Redox Kinetics Simulator studies."""
    repo = BiohybridMicrobialFuelCellRedoxRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=BiohybridMicrobialFuelCellRedoxStudyResponse)
async def get_biohybrid_microbial_fuel_cell_redox_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Biohybrid Microbial Fuel Cell Extracellular Electron Shuttle Redox Kinetics Simulator study by ID."""
    repo = BiohybridMicrobialFuelCellRedoxRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
