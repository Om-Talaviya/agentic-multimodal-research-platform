"""FastAPI routes for Phase 544: Autonomous Integrated Cryo-CLEM High-Precision 3D Sub-Diffraction Nanoscale Fiducial Correlator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.cryo_correlative_light_electron_tomography_clem_repo import CryoCorrelativeLightElectronTomographyClemRepository
from research.orchestration.cryo_correlative_light_electron_tomography_clem_engine import CryoCorrelativeLightElectronTomographyClemEngine

router = APIRouter(prefix="/cryo-correlative-light-electron-tomography-clem", tags=["cryo-correlative-light-electron-tomography-clem"])


class AnalyzeCryoCorrelativeLightElectronTomographyClemRequest(BaseModel):
    name: str = Field(..., example="Autonomous Integrated Cryo-CLEM High-Precision 3D Sub-Diffraction Nanoscale Fiducial Correlator Run")
    target_specimen: str = Field(default="Cryo-Vitrified Neuronal Cultured Grid with Tetraspeck Fluorescent Nanobeads and Sub-10nm Gold Fiducials")
    analytical_modality: str = Field(default="cryo-clem-fiducial-correlation")
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


class CryoCorrelativeLightElectronTomographyClemStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    cross_modality_3d_registration_precision_nm: float
    cryo_fluorescence_signal_to_background_ratio: float
    cryo_fib_milling_target_accuracy_nm: float
    subtomogram_correlation_coefficient: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=CryoCorrelativeLightElectronTomographyClemStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_cryo_correlative_light_electron_tomography_clem(
    req: AnalyzeCryoCorrelativeLightElectronTomographyClemRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Integrated Cryo-CLEM High-Precision 3D Sub-Diffraction Nanoscale Fiducial Correlator analysis and persist study."""
    engine = CryoCorrelativeLightElectronTomographyClemEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = CryoCorrelativeLightElectronTomographyClemRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        cross_modality_3d_registration_precision_nm=result.cross_modality_3d_registration_precision_nm,
        cryo_fluorescence_signal_to_background_ratio=result.cryo_fluorescence_signal_to_background_ratio,
        cryo_fib_milling_target_accuracy_nm=result.cryo_fib_milling_target_accuracy_nm,
        subtomogram_correlation_coefficient=result.subtomogram_correlation_coefficient,
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

    return CryoCorrelativeLightElectronTomographyClemStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        cross_modality_3d_registration_precision_nm=study.cross_modality_3d_registration_precision_nm,
        cryo_fluorescence_signal_to_background_ratio=study.cryo_fluorescence_signal_to_background_ratio,
        cryo_fib_milling_target_accuracy_nm=study.cryo_fib_milling_target_accuracy_nm,
        subtomogram_correlation_coefficient=study.subtomogram_correlation_coefficient,
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


@router.get("/studies", response_model=List[CryoCorrelativeLightElectronTomographyClemStudyResponse])
async def list_cryo_correlative_light_electron_tomography_clem_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Integrated Cryo-CLEM High-Precision 3D Sub-Diffraction Nanoscale Fiducial Correlator studies."""
    repo = CryoCorrelativeLightElectronTomographyClemRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=CryoCorrelativeLightElectronTomographyClemStudyResponse)
async def get_cryo_correlative_light_electron_tomography_clem_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Integrated Cryo-CLEM High-Precision 3D Sub-Diffraction Nanoscale Fiducial Correlator study by ID."""
    repo = CryoCorrelativeLightElectronTomographyClemRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
