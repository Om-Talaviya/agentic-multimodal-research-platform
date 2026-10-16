"""FastAPI route for Phase 569: Autonomous In-Situ Cryo-Correlative Super-Resolution Cryo-Fluorescence & Cryo-ET Single-Molecule Spatial Registration Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.super_resolution_cryo_fluorescence_correlator_repo import SuperResolutionCryoFluorescenceCorrelatorRepository
from research.orchestration.super_resolution_cryo_fluorescence_correlator_engine import SuperResolutionCryoFluorescenceCorrelatorEngine

router = APIRouter(prefix="/super-resolution-cryo-fluorescence-correlator", tags=["Phase 569 - Autonomous In-Situ Cryo-Correlative Super-Resolution Cryo-Fluorescence & Cryo-ET Single-Molecule Spatial Registration Engine"])


class SuperResolutionCryoFluorescenceCorrelatorAnalyzeRequest(BaseModel):
    name: str = Field(default="Autonomous In-Situ Cryo-Correlative Super-Resolution Cryo-Fluorescence & Cryo-ET Single-Molecule Spatial Registration Engine Study")
    target_specimen: Optional[str] = Field(default="Vitrified Mammalian HeLa Lamella with Cryo-Photoswitchable mEos4b Fluorophores and Gold Nanoparticle Fiducials")
    analytical_modality: Optional[str] = Field(default="cryo-super-resolution-registration")
    input_scale: float = Field(default=1.0, ge=0.1, le=10.0)


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


class SuperResolutionCryoFluorescenceCorrelatorStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    fiducial_registration_precision_nm: float
    photobleaching_threshold_flux_kw_cm2: float
    localization_confidence_score: float
    cryo_optical_drift_variance_nm2: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []


@router.post("/analyze", response_model=SuperResolutionCryoFluorescenceCorrelatorStudyResponse)
async def analyze_super_resolution_cryo_fluorescence_correlator(
    req: SuperResolutionCryoFluorescenceCorrelatorAnalyzeRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Execute autonomous analysis for Autonomous In-Situ Cryo-Correlative Super-Resolution Cryo-Fluorescence & Cryo-ET Single-Molecule Spatial Registration Engine."""
    engine = SuperResolutionCryoFluorescenceCorrelatorEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SuperResolutionCryoFluorescenceCorrelatorRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        fiducial_registration_precision_nm=result.fiducial_registration_precision_nm,
        photobleaching_threshold_flux_kw_cm2=result.photobleaching_threshold_flux_kw_cm2,
        localization_confidence_score=result.localization_confidence_score,
        cryo_optical_drift_variance_nm2=result.cryo_optical_drift_variance_nm2,
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

    return SuperResolutionCryoFluorescenceCorrelatorStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        fiducial_registration_precision_nm=study.fiducial_registration_precision_nm,
        photobleaching_threshold_flux_kw_cm2=study.photobleaching_threshold_flux_kw_cm2,
        localization_confidence_score=study.localization_confidence_score,
        cryo_optical_drift_variance_nm2=study.cryo_optical_drift_variance_nm2,
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


@router.get("/studies", response_model=List[SuperResolutionCryoFluorescenceCorrelatorStudyResponse])
async def list_super_resolution_cryo_fluorescence_correlator_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous In-Situ Cryo-Correlative Super-Resolution Cryo-Fluorescence & Cryo-ET Single-Molecule Spatial Registration Engine studies."""
    repo = SuperResolutionCryoFluorescenceCorrelatorRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SuperResolutionCryoFluorescenceCorrelatorStudyResponse)
async def get_super_resolution_cryo_fluorescence_correlator_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous In-Situ Cryo-Correlative Super-Resolution Cryo-Fluorescence & Cryo-ET Single-Molecule Spatial Registration Engine study by ID."""
    repo = SuperResolutionCryoFluorescenceCorrelatorRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
