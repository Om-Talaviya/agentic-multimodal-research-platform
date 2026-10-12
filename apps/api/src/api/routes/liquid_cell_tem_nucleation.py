"""FastAPI routes for Phase 428: Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy (LC-TEM) Nanoparticle Nucleation Simulator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.liquid_cell_tem_nucleation_repo import LiquidCellTemNucleationRepository
from research.orchestration.liquid_cell_tem_nucleation_engine import LiquidCellTemNucleationEngine

router = APIRouter(prefix="/liquid-cell-tem-nucleation", tags=["liquid-cell-tem-nucleation"])


class AnalyzeLiquidCellTemNucleationRequest(BaseModel):
    name: str = Field(..., example="Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy (LC-TEM) Nanoparticle Nucleation Simulator Run")
    target_specimen: str = Field(default="Silicon Nitride Liquid Cell with Gold Nanocrystal Growth Solution")
    analytical_modality: str = Field(default="liquid-cell-tem")
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


class LiquidCellTemNucleationStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    nucleation_rate_particles_per_s_um2: float
    critical_nucleus_radius_nm: float
    non_classical_attachment_frequency: float
    electron_beam_dose_rate_e_per_ang2_s: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=LiquidCellTemNucleationStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_liquid_cell_tem_nucleation(
    req: AnalyzeLiquidCellTemNucleationRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy (LC-TEM) Nanoparticle Nucleation Simulator analysis and persist study."""
    engine = LiquidCellTemNucleationEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = LiquidCellTemNucleationRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        nucleation_rate_particles_per_s_um2=result.nucleation_rate_particles_per_s_um2,
        critical_nucleus_radius_nm=result.critical_nucleus_radius_nm,
        non_classical_attachment_frequency=result.non_classical_attachment_frequency,
        electron_beam_dose_rate_e_per_ang2_s=result.electron_beam_dose_rate_e_per_ang2_s,
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

    return LiquidCellTemNucleationStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        nucleation_rate_particles_per_s_um2=study.nucleation_rate_particles_per_s_um2,
        critical_nucleus_radius_nm=study.critical_nucleus_radius_nm,
        non_classical_attachment_frequency=study.non_classical_attachment_frequency,
        electron_beam_dose_rate_e_per_ang2_s=study.electron_beam_dose_rate_e_per_ang2_s,
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


@router.get("/studies", response_model=List[LiquidCellTemNucleationStudyResponse])
async def list_liquid_cell_tem_nucleation_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy (LC-TEM) Nanoparticle Nucleation Simulator studies."""
    repo = LiquidCellTemNucleationRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=LiquidCellTemNucleationStudyResponse)
async def get_liquid_cell_tem_nucleation_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy (LC-TEM) Nanoparticle Nucleation Simulator study by ID."""
    repo = LiquidCellTemNucleationRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
