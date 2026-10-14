"""FastAPI routes for Phase 524: Autonomous Picoliter Microfluidic Droplet Single-Cell Mass Spectrometry Proteome Fingerprinter."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.droplet_single_cell_mass_spec_proteomics_repo import DropletSingleCellMassSpecProteomicsRepository
from research.orchestration.droplet_single_cell_mass_spec_proteomics_engine import DropletSingleCellMassSpecProteomicsEngine

router = APIRouter(prefix="/droplet-single-cell-mass-spec-proteomics", tags=["droplet-single-cell-mass-spec-proteomics"])


class AnalyzeDropletSingleCellMassSpecProteomicsRequest(BaseModel):
    name: str = Field(..., example="Autonomous Picoliter Microfluidic Droplet Single-Cell Mass Spectrometry Proteome Fingerprinter Run")
    target_specimen: str = Field(default="Direct Microfluidic Nano-Electrospray Ionization (nanoESI) Orbitrap MS of Individual Single Glioblastoma Cells")
    analytical_modality: str = Field(default="droplet-single-cell-proteomics")
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


class DropletSingleCellMassSpecProteomicsStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    quantified_proteins_per_single_cell_count: float
    median_protein_sequence_coverage_pct: float
    sample_loss_reduction_surface_adsorption_pct: float
    single_cell_proteomic_profiling_throughput_cells_per_hr: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=DropletSingleCellMassSpecProteomicsStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_droplet_single_cell_mass_spec_proteomics(
    req: AnalyzeDropletSingleCellMassSpecProteomicsRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Picoliter Microfluidic Droplet Single-Cell Mass Spectrometry Proteome Fingerprinter analysis and persist study."""
    engine = DropletSingleCellMassSpecProteomicsEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = DropletSingleCellMassSpecProteomicsRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        quantified_proteins_per_single_cell_count=result.quantified_proteins_per_single_cell_count,
        median_protein_sequence_coverage_pct=result.median_protein_sequence_coverage_pct,
        sample_loss_reduction_surface_adsorption_pct=result.sample_loss_reduction_surface_adsorption_pct,
        single_cell_proteomic_profiling_throughput_cells_per_hr=result.single_cell_proteomic_profiling_throughput_cells_per_hr,
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

    return DropletSingleCellMassSpecProteomicsStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        quantified_proteins_per_single_cell_count=study.quantified_proteins_per_single_cell_count,
        median_protein_sequence_coverage_pct=study.median_protein_sequence_coverage_pct,
        sample_loss_reduction_surface_adsorption_pct=study.sample_loss_reduction_surface_adsorption_pct,
        single_cell_proteomic_profiling_throughput_cells_per_hr=study.single_cell_proteomic_profiling_throughput_cells_per_hr,
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


@router.get("/studies", response_model=List[DropletSingleCellMassSpecProteomicsStudyResponse])
async def list_droplet_single_cell_mass_spec_proteomics_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Picoliter Microfluidic Droplet Single-Cell Mass Spectrometry Proteome Fingerprinter studies."""
    repo = DropletSingleCellMassSpecProteomicsRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=DropletSingleCellMassSpecProteomicsStudyResponse)
async def get_droplet_single_cell_mass_spec_proteomics_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Picoliter Microfluidic Droplet Single-Cell Mass Spectrometry Proteome Fingerprinter study by ID."""
    repo = DropletSingleCellMassSpecProteomicsRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
