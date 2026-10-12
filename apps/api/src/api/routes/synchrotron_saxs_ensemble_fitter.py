"""FastAPI routes for Phase 433: Autonomous Synchrotron Small-Angle X-ray Scattering (SAXS) Ensemble Conformational Fitting Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.synchrotron_saxs_ensemble_fitter_repo import SynchrotronSaxsEnsembleFitterRepository
from research.orchestration.synchrotron_saxs_ensemble_fitter_engine import SynchrotronSaxsEnsembleFitterEngine

router = APIRouter(prefix="/synchrotron-saxs-ensemble-fitter", tags=["synchrotron-saxs-ensemble-fitter"])


class AnalyzeSynchrotronSaxsEnsembleFitterRequest(BaseModel):
    name: str = Field(..., example="Autonomous Synchrotron Small-Angle X-ray Scattering (SAXS) Ensemble Conformational Fitting Engine Run")
    target_specimen: str = Field(default="Intrinsically Disordered Kinase Domain in Solution")
    analytical_modality: str = Field(default="synchrotron-saxs")
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


class SynchrotronSaxsEnsembleFitterStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    radius_of_gyration_Rg_angstrom: float
    kratky_plot_flexibility_index: float
    ensemble_fit_chi_squared: float
    maximum_particle_dimension_Dmax_angstrom: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=SynchrotronSaxsEnsembleFitterStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_synchrotron_saxs_ensemble_fitter(
    req: AnalyzeSynchrotronSaxsEnsembleFitterRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Synchrotron Small-Angle X-ray Scattering (SAXS) Ensemble Conformational Fitting Engine analysis and persist study."""
    engine = SynchrotronSaxsEnsembleFitterEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SynchrotronSaxsEnsembleFitterRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        radius_of_gyration_Rg_angstrom=result.radius_of_gyration_Rg_angstrom,
        kratky_plot_flexibility_index=result.kratky_plot_flexibility_index,
        ensemble_fit_chi_squared=result.ensemble_fit_chi_squared,
        maximum_particle_dimension_Dmax_angstrom=result.maximum_particle_dimension_Dmax_angstrom,
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

    return SynchrotronSaxsEnsembleFitterStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        radius_of_gyration_Rg_angstrom=study.radius_of_gyration_Rg_angstrom,
        kratky_plot_flexibility_index=study.kratky_plot_flexibility_index,
        ensemble_fit_chi_squared=study.ensemble_fit_chi_squared,
        maximum_particle_dimension_Dmax_angstrom=study.maximum_particle_dimension_Dmax_angstrom,
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


@router.get("/studies", response_model=List[SynchrotronSaxsEnsembleFitterStudyResponse])
async def list_synchrotron_saxs_ensemble_fitter_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Synchrotron Small-Angle X-ray Scattering (SAXS) Ensemble Conformational Fitting Engine studies."""
    repo = SynchrotronSaxsEnsembleFitterRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SynchrotronSaxsEnsembleFitterStudyResponse)
async def get_synchrotron_saxs_ensemble_fitter_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Synchrotron Small-Angle X-ray Scattering (SAXS) Ensemble Conformational Fitting Engine study by ID."""
    repo = SynchrotronSaxsEnsembleFitterRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
