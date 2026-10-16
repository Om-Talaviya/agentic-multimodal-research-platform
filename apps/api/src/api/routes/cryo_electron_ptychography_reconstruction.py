"""FastAPI routes for Phase 548: Autonomous In-Cell Cryo-Electron Ptychography Phase-Plate Macromolecular Reconstruction Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.cryo_electron_ptychography_reconstruction_repo import CryoElectronPtychographyReconstructionRepository
from research.orchestration.cryo_electron_ptychography_reconstruction_engine import CryoElectronPtychographyReconstructionEngine

router = APIRouter(prefix="/cryo-electron-ptychography-reconstruction", tags=["cryo-electron-ptychography-reconstruction"])


class AnalyzeCryoElectronPtychographyReconstructionRequest(BaseModel):
    name: str = Field(..., example="Autonomous In-Cell Cryo-Electron Ptychography Phase-Plate Macromolecular Reconstruction Engine Run")
    target_specimen: str = Field(default="Intact Vitrified Chlamydomonas reinhardtii Chloroplast Membrane Thylakoid with Fast Direct Electron Camera 4D-STEM")
    analytical_modality: str = Field(default="cryo-ptychography-4d-stem")
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


class CryoElectronPtychographyReconstructionStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    sub_angstrom_phase_contrast_resolution_a: float
    inelastic_mean_free_path_depth_nm: float
    dose_efficiency_snr_gain_factor: float
    phase_plate_wavefront_aberration_mrad: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=CryoElectronPtychographyReconstructionStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_cryo_electron_ptychography_reconstruction(
    req: AnalyzeCryoElectronPtychographyReconstructionRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous In-Cell Cryo-Electron Ptychography Phase-Plate Macromolecular Reconstruction Engine analysis and persist study."""
    engine = CryoElectronPtychographyReconstructionEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = CryoElectronPtychographyReconstructionRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        sub_angstrom_phase_contrast_resolution_a=result.sub_angstrom_phase_contrast_resolution_a,
        inelastic_mean_free_path_depth_nm=result.inelastic_mean_free_path_depth_nm,
        dose_efficiency_snr_gain_factor=result.dose_efficiency_snr_gain_factor,
        phase_plate_wavefront_aberration_mrad=result.phase_plate_wavefront_aberration_mrad,
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

    return CryoElectronPtychographyReconstructionStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        sub_angstrom_phase_contrast_resolution_a=study.sub_angstrom_phase_contrast_resolution_a,
        inelastic_mean_free_path_depth_nm=study.inelastic_mean_free_path_depth_nm,
        dose_efficiency_snr_gain_factor=study.dose_efficiency_snr_gain_factor,
        phase_plate_wavefront_aberration_mrad=study.phase_plate_wavefront_aberration_mrad,
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


@router.get("/studies", response_model=List[CryoElectronPtychographyReconstructionStudyResponse])
async def list_cryo_electron_ptychography_reconstruction_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous In-Cell Cryo-Electron Ptychography Phase-Plate Macromolecular Reconstruction Engine studies."""
    repo = CryoElectronPtychographyReconstructionRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=CryoElectronPtychographyReconstructionStudyResponse)
async def get_cryo_electron_ptychography_reconstruction_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous In-Cell Cryo-Electron Ptychography Phase-Plate Macromolecular Reconstruction Engine study by ID."""
    repo = CryoElectronPtychographyReconstructionRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
