"""FastAPI routes for Phase 516: Autonomous Automated High-Throughput Mass Photometry Macromolecular Mass Dispersity Profiler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.high_throughput_mass_photometry_ribosome_repo import HighThroughputMassPhotometryRibosomeRepository
from research.orchestration.high_throughput_mass_photometry_ribosome_engine import HighThroughputMassPhotometryRibosomeEngine

router = APIRouter(prefix="/high-throughput-mass-photometry-ribosome", tags=["high-throughput-mass-photometry-ribosome"])


class AnalyzeHighThroughputMassPhotometryRibosomeRequest(BaseModel):
    name: str = Field(..., example="Autonomous Automated High-Throughput Mass Photometry Macromolecular Mass Dispersity Profiler Run")
    target_specimen: str = Field(default="Label-Free Reconstituted 70S Ribosome Assembly Intermediates with Initiation Factors IF1/IF2/IF3")
    analytical_modality: str = Field(default="mass-photometry-single-molecule-scattering")
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


class HighThroughputMassPhotometryRibosomeStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    molecular_mass_resolution_error_pct: float
    subassembly_stoichiometric_ratio_30s_50s_70s: float
    single_molecule_scattering_interferometric_contrast: float
    sample_consumption_volume_nanoliters: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=HighThroughputMassPhotometryRibosomeStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_high_throughput_mass_photometry_ribosome(
    req: AnalyzeHighThroughputMassPhotometryRibosomeRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Automated High-Throughput Mass Photometry Macromolecular Mass Dispersity Profiler analysis and persist study."""
    engine = HighThroughputMassPhotometryRibosomeEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = HighThroughputMassPhotometryRibosomeRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        molecular_mass_resolution_error_pct=result.molecular_mass_resolution_error_pct,
        subassembly_stoichiometric_ratio_30s_50s_70s=result.subassembly_stoichiometric_ratio_30s_50s_70s,
        single_molecule_scattering_interferometric_contrast=result.single_molecule_scattering_interferometric_contrast,
        sample_consumption_volume_nanoliters=result.sample_consumption_volume_nanoliters,
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

    return HighThroughputMassPhotometryRibosomeStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        molecular_mass_resolution_error_pct=study.molecular_mass_resolution_error_pct,
        subassembly_stoichiometric_ratio_30s_50s_70s=study.subassembly_stoichiometric_ratio_30s_50s_70s,
        single_molecule_scattering_interferometric_contrast=study.single_molecule_scattering_interferometric_contrast,
        sample_consumption_volume_nanoliters=study.sample_consumption_volume_nanoliters,
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


@router.get("/studies", response_model=List[HighThroughputMassPhotometryRibosomeStudyResponse])
async def list_high_throughput_mass_photometry_ribosome_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Automated High-Throughput Mass Photometry Macromolecular Mass Dispersity Profiler studies."""
    repo = HighThroughputMassPhotometryRibosomeRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=HighThroughputMassPhotometryRibosomeStudyResponse)
async def get_high_throughput_mass_photometry_ribosome_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Automated High-Throughput Mass Photometry Macromolecular Mass Dispersity Profiler study by ID."""
    repo = HighThroughputMassPhotometryRibosomeRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
