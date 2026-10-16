"""FastAPI routes for Phase 561: Autonomous High-Throughput Deep Ocean Hydrothermal Vent Metagenomic Novel Enzyme Prospector."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.ocean_hydrothermal_metagenomic_enzyme_prospector_repo import OceanHydrothermalMetagenomicEnzymeProspectorRepository
from research.orchestration.ocean_hydrothermal_metagenomic_enzyme_prospector_engine import OceanHydrothermalMetagenomicEnzymeProspectorEngine

router = APIRouter(prefix="/ocean-hydrothermal-metagenomic-enzyme-prospector", tags=["ocean-hydrothermal-metagenomic-enzyme-prospector"])


class AnalyzeOceanHydrothermalMetagenomicEnzymeProspectorRequest(BaseModel):
    name: str = Field(..., example="Autonomous High-Throughput Deep Ocean Hydrothermal Vent Metagenomic Novel Enzyme Prospector Run")
    target_specimen: str = Field(default="Deep-Sea Metagenomic DNA from Mid-Atlantic Ridge Black Smoker Vent Hydrothermal Fluid at 320C and 300 Bar")
    analytical_modality: str = Field(default="deep-sea-metagenomic-biocatalysis")
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


class OceanHydrothermalMetagenomicEnzymeProspectorStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    thermostable_extremozyme_catalytic_half_life_hours: float
    novel_biocatalytic_family_discovery_count: float
    piezophilic_activation_volume_delta_v_ml_mol: float
    optimum_catalytic_temperature_celsius: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=OceanHydrothermalMetagenomicEnzymeProspectorStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_ocean_hydrothermal_metagenomic_enzyme_prospector(
    req: AnalyzeOceanHydrothermalMetagenomicEnzymeProspectorRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous High-Throughput Deep Ocean Hydrothermal Vent Metagenomic Novel Enzyme Prospector analysis and persist study."""
    engine = OceanHydrothermalMetagenomicEnzymeProspectorEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = OceanHydrothermalMetagenomicEnzymeProspectorRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        thermostable_extremozyme_catalytic_half_life_hours=result.thermostable_extremozyme_catalytic_half_life_hours,
        novel_biocatalytic_family_discovery_count=result.novel_biocatalytic_family_discovery_count,
        piezophilic_activation_volume_delta_v_ml_mol=result.piezophilic_activation_volume_delta_v_ml_mol,
        optimum_catalytic_temperature_celsius=result.optimum_catalytic_temperature_celsius,
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

    return OceanHydrothermalMetagenomicEnzymeProspectorStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        thermostable_extremozyme_catalytic_half_life_hours=study.thermostable_extremozyme_catalytic_half_life_hours,
        novel_biocatalytic_family_discovery_count=study.novel_biocatalytic_family_discovery_count,
        piezophilic_activation_volume_delta_v_ml_mol=study.piezophilic_activation_volume_delta_v_ml_mol,
        optimum_catalytic_temperature_celsius=study.optimum_catalytic_temperature_celsius,
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


@router.get("/studies", response_model=List[OceanHydrothermalMetagenomicEnzymeProspectorStudyResponse])
async def list_ocean_hydrothermal_metagenomic_enzyme_prospector_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous High-Throughput Deep Ocean Hydrothermal Vent Metagenomic Novel Enzyme Prospector studies."""
    repo = OceanHydrothermalMetagenomicEnzymeProspectorRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=OceanHydrothermalMetagenomicEnzymeProspectorStudyResponse)
async def get_ocean_hydrothermal_metagenomic_enzyme_prospector_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous High-Throughput Deep Ocean Hydrothermal Vent Metagenomic Novel Enzyme Prospector study by ID."""
    repo = OceanHydrothermalMetagenomicEnzymeProspectorRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
