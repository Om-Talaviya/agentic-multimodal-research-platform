"""FastAPI routes for Phase 473: Autonomous Bio-Piezoelectric Cell Membrane Flexoelectric Curvature Transduction Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.flexoelectric_membrane_curvature_repo import FlexoelectricMembraneCurvatureRepository
from research.orchestration.flexoelectric_membrane_curvature_engine import FlexoelectricMembraneCurvatureEngine

router = APIRouter(prefix="/flexoelectric-membrane-curvature", tags=["flexoelectric-membrane-curvature"])


class AnalyzeFlexoelectricMembraneCurvatureRequest(BaseModel):
    name: str = Field(..., example="Autonomous Bio-Piezoelectric Cell Membrane Flexoelectric Curvature Transduction Engine Run")
    target_specimen: str = Field(default="Asymmetric Phospholipid Bilayer Giant Unilamellar Vesicle with Micropipette Aspiration Curvature")
    analytical_modality: str = Field(default="flexoelectric-membrane-curvature")
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


class FlexoelectricMembraneCurvatureStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    flexoelectric_coupling_coefficient_pC_per_m: float
    membrane_curvature_radius_nm: float
    transmembrane_induced_polarization_potential_mV: float
    lipid_dipole_reorientation_energy_kj_mol: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=FlexoelectricMembraneCurvatureStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_flexoelectric_membrane_curvature(
    req: AnalyzeFlexoelectricMembraneCurvatureRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Bio-Piezoelectric Cell Membrane Flexoelectric Curvature Transduction Engine analysis and persist study."""
    engine = FlexoelectricMembraneCurvatureEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = FlexoelectricMembraneCurvatureRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        flexoelectric_coupling_coefficient_pC_per_m=result.flexoelectric_coupling_coefficient_pC_per_m,
        membrane_curvature_radius_nm=result.membrane_curvature_radius_nm,
        transmembrane_induced_polarization_potential_mV=result.transmembrane_induced_polarization_potential_mV,
        lipid_dipole_reorientation_energy_kj_mol=result.lipid_dipole_reorientation_energy_kj_mol,
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

    return FlexoelectricMembraneCurvatureStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        flexoelectric_coupling_coefficient_pC_per_m=study.flexoelectric_coupling_coefficient_pC_per_m,
        membrane_curvature_radius_nm=study.membrane_curvature_radius_nm,
        transmembrane_induced_polarization_potential_mV=study.transmembrane_induced_polarization_potential_mV,
        lipid_dipole_reorientation_energy_kj_mol=study.lipid_dipole_reorientation_energy_kj_mol,
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


@router.get("/studies", response_model=List[FlexoelectricMembraneCurvatureStudyResponse])
async def list_flexoelectric_membrane_curvature_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Bio-Piezoelectric Cell Membrane Flexoelectric Curvature Transduction Engine studies."""
    repo = FlexoelectricMembraneCurvatureRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=FlexoelectricMembraneCurvatureStudyResponse)
async def get_flexoelectric_membrane_curvature_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Bio-Piezoelectric Cell Membrane Flexoelectric Curvature Transduction Engine study by ID."""
    repo = FlexoelectricMembraneCurvatureRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
