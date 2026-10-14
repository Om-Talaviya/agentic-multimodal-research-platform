"""FastAPI routes for Phase 520: Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy Protein Nucleation Real-Time Tracker."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.liquid_cell_tem_protein_crystallization_repo import LiquidCellTemProteinCrystallizationRepository
from research.orchestration.liquid_cell_tem_protein_crystallization_engine import LiquidCellTemProteinCrystallizationEngine

router = APIRouter(prefix="/liquid-cell-tem-protein-crystallization", tags=["liquid-cell-tem-protein-crystallization"])


class AnalyzeLiquidCellTemProteinCrystallizationRequest(BaseModel):
    name: str = Field(..., example="Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy Protein Nucleation Real-Time Tracker Run")
    target_specimen: str = Field(default="Silicon Nitride Microchip Graphene Liquid Cell with Supersaturated Hen Egg-White Lysozyme Solution")
    analytical_modality: str = Field(default="liquid-cell-tem-crystallization")
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


class LiquidCellTemProteinCrystallizationStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    critical_nucleus_radius_nm: float
    non_classical_pre_nucleation_cluster_density_per_um3: float
    crystal_facet_growth_rate_nm_per_min: float
    electron_beam_dose_induced_radiolysis_damage_threshold_e_per_angstrom2: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=LiquidCellTemProteinCrystallizationStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_liquid_cell_tem_protein_crystallization(
    req: AnalyzeLiquidCellTemProteinCrystallizationRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy Protein Nucleation Real-Time Tracker analysis and persist study."""
    engine = LiquidCellTemProteinCrystallizationEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = LiquidCellTemProteinCrystallizationRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        critical_nucleus_radius_nm=result.critical_nucleus_radius_nm,
        non_classical_pre_nucleation_cluster_density_per_um3=result.non_classical_pre_nucleation_cluster_density_per_um3,
        crystal_facet_growth_rate_nm_per_min=result.crystal_facet_growth_rate_nm_per_min,
        electron_beam_dose_induced_radiolysis_damage_threshold_e_per_angstrom2=result.electron_beam_dose_induced_radiolysis_damage_threshold_e_per_angstrom2,
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

    return LiquidCellTemProteinCrystallizationStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        critical_nucleus_radius_nm=study.critical_nucleus_radius_nm,
        non_classical_pre_nucleation_cluster_density_per_um3=study.non_classical_pre_nucleation_cluster_density_per_um3,
        crystal_facet_growth_rate_nm_per_min=study.crystal_facet_growth_rate_nm_per_min,
        electron_beam_dose_induced_radiolysis_damage_threshold_e_per_angstrom2=study.electron_beam_dose_induced_radiolysis_damage_threshold_e_per_angstrom2,
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


@router.get("/studies", response_model=List[LiquidCellTemProteinCrystallizationStudyResponse])
async def list_liquid_cell_tem_protein_crystallization_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy Protein Nucleation Real-Time Tracker studies."""
    repo = LiquidCellTemProteinCrystallizationRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=LiquidCellTemProteinCrystallizationStudyResponse)
async def get_liquid_cell_tem_protein_crystallization_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous In-Situ Liquid-Cell Transmission Electron Microscopy Protein Nucleation Real-Time Tracker study by ID."""
    repo = LiquidCellTemProteinCrystallizationRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
