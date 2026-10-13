"""FastAPI routes for Phase 449: Autonomous Microfluidic Droplet Single-Cell Metabolic Metabolomics Isotope Labeling Profiler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.droplet_single_cell_isotope_metabolomics_repo import DropletSingleCellIsotopeMetabolomicsRepository
from research.orchestration.droplet_single_cell_isotope_metabolomics_engine import DropletSingleCellIsotopeMetabolomicsEngine

router = APIRouter(prefix="/droplet-single-cell-metabolomics", tags=["droplet-single-cell-metabolomics"])


class AnalyzeDropletSingleCellIsotopeMetabolomicsRequest(BaseModel):
    name: str = Field(..., example="Autonomous Microfluidic Droplet Single-Cell Metabolic Metabolomics Isotope Labeling Profiler Run")
    target_specimen: str = Field(default="Glucose-13C6 Labeled Glioblastoma Stem-Like Cells in Monodisperse Fluorocarbon Droplets")
    analytical_modality: str = Field(default="single-cell-droplet-metabolomics")
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


class DropletSingleCellIsotopeMetabolomicsStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    isotopic_enrichment_m3_lactate_ratio: float
    droplet_generation_frequency_khz: float
    glycolytic_flux_attomoles_per_cell_min: float
    mass_accuracy_orbitrap_ppm: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=DropletSingleCellIsotopeMetabolomicsStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_droplet_single_cell_isotope_metabolomics(
    req: AnalyzeDropletSingleCellIsotopeMetabolomicsRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Microfluidic Droplet Single-Cell Metabolic Metabolomics Isotope Labeling Profiler analysis and persist study."""
    engine = DropletSingleCellIsotopeMetabolomicsEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = DropletSingleCellIsotopeMetabolomicsRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        isotopic_enrichment_m3_lactate_ratio=result.isotopic_enrichment_m3_lactate_ratio,
        droplet_generation_frequency_khz=result.droplet_generation_frequency_khz,
        glycolytic_flux_attomoles_per_cell_min=result.glycolytic_flux_attomoles_per_cell_min,
        mass_accuracy_orbitrap_ppm=result.mass_accuracy_orbitrap_ppm,
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

    return DropletSingleCellIsotopeMetabolomicsStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        isotopic_enrichment_m3_lactate_ratio=study.isotopic_enrichment_m3_lactate_ratio,
        droplet_generation_frequency_khz=study.droplet_generation_frequency_khz,
        glycolytic_flux_attomoles_per_cell_min=study.glycolytic_flux_attomoles_per_cell_min,
        mass_accuracy_orbitrap_ppm=study.mass_accuracy_orbitrap_ppm,
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


@router.get("/studies", response_model=List[DropletSingleCellIsotopeMetabolomicsStudyResponse])
async def list_droplet_single_cell_isotope_metabolomics_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Microfluidic Droplet Single-Cell Metabolic Metabolomics Isotope Labeling Profiler studies."""
    repo = DropletSingleCellIsotopeMetabolomicsRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=DropletSingleCellIsotopeMetabolomicsStudyResponse)
async def get_droplet_single_cell_isotope_metabolomics_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Microfluidic Droplet Single-Cell Metabolic Metabolomics Isotope Labeling Profiler study by ID."""
    repo = DropletSingleCellIsotopeMetabolomicsRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
