"""FastAPI routes for Phase 555: Autonomous Microfluidic High-Pressure Supercritical Fluid Nanoparticle Encapsulation Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.supercritical_fluid_nanoparticle_encapsulation_repo import SupercriticalFluidNanoparticleEncapsulationRepository
from research.orchestration.supercritical_fluid_nanoparticle_encapsulation_engine import SupercriticalFluidNanoparticleEncapsulationEngine

router = APIRouter(prefix="/supercritical-fluid-nanoparticle-encapsulation", tags=["supercritical-fluid-nanoparticle-encapsulation"])


class AnalyzeSupercriticalFluidNanoparticleEncapsulationRequest(BaseModel):
    name: str = Field(..., example="Autonomous Microfluidic High-Pressure Supercritical Fluid Nanoparticle Encapsulation Engine Run")
    target_specimen: str = Field(default="Supercritical CO2 Rapid Expansion (RESS-SC) of PLGA-PEG Encapsulating Hydrophobic Paclitaxel and Cy5.5 Nanotracers")
    analytical_modality: str = Field(default="supercritical-fluid-nanoparticle")
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


class SupercriticalFluidNanoparticleEncapsulationStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    nanoparticle_mean_hydrodynamic_diameter_nm: float
    encapsulation_efficiency_payload_pct: float
    polydispersity_index_pdi: float
    supercritical_operating_pressure_bar: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=SupercriticalFluidNanoparticleEncapsulationStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_supercritical_fluid_nanoparticle_encapsulation(
    req: AnalyzeSupercriticalFluidNanoparticleEncapsulationRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Microfluidic High-Pressure Supercritical Fluid Nanoparticle Encapsulation Engine analysis and persist study."""
    engine = SupercriticalFluidNanoparticleEncapsulationEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SupercriticalFluidNanoparticleEncapsulationRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        nanoparticle_mean_hydrodynamic_diameter_nm=result.nanoparticle_mean_hydrodynamic_diameter_nm,
        encapsulation_efficiency_payload_pct=result.encapsulation_efficiency_payload_pct,
        polydispersity_index_pdi=result.polydispersity_index_pdi,
        supercritical_operating_pressure_bar=result.supercritical_operating_pressure_bar,
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

    return SupercriticalFluidNanoparticleEncapsulationStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        nanoparticle_mean_hydrodynamic_diameter_nm=study.nanoparticle_mean_hydrodynamic_diameter_nm,
        encapsulation_efficiency_payload_pct=study.encapsulation_efficiency_payload_pct,
        polydispersity_index_pdi=study.polydispersity_index_pdi,
        supercritical_operating_pressure_bar=study.supercritical_operating_pressure_bar,
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


@router.get("/studies", response_model=List[SupercriticalFluidNanoparticleEncapsulationStudyResponse])
async def list_supercritical_fluid_nanoparticle_encapsulation_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Microfluidic High-Pressure Supercritical Fluid Nanoparticle Encapsulation Engine studies."""
    repo = SupercriticalFluidNanoparticleEncapsulationRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SupercriticalFluidNanoparticleEncapsulationStudyResponse)
async def get_supercritical_fluid_nanoparticle_encapsulation_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Microfluidic High-Pressure Supercritical Fluid Nanoparticle Encapsulation Engine study by ID."""
    repo = SupercriticalFluidNanoparticleEncapsulationRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
