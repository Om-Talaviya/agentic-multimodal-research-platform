"""FastAPI routes for Phase 565: Autonomous Quantum Entangled Photon Biological Tissue Multiphoton Imaging Resolution Maximizer."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.quantum_entangled_photon_multiphoton_imaging_repo import QuantumEntangledPhotonMultiphotonImagingRepository
from research.orchestration.quantum_entangled_photon_multiphoton_imaging_engine import QuantumEntangledPhotonMultiphotonImagingEngine

router = APIRouter(prefix="/quantum-entangled-photon-multiphoton-imaging", tags=["quantum-entangled-photon-multiphoton-imaging"])


class AnalyzeQuantumEntangledPhotonMultiphotonImagingRequest(BaseModel):
    name: str = Field(..., example="Autonomous Quantum Entangled Photon Biological Tissue Multiphoton Imaging Resolution Maximizer Run")
    target_specimen: str = Field(default="Intact Vitrified Mouse Cortical Brain Slices illuminated with Polarization-Entangled Photon Pairs at 800nm")
    analytical_modality: str = Field(default="entangled-photon-multiphoton")
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


class QuantumEntangledPhotonMultiphotonImagingStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    two_photon_absorption_cross_section_enhancement_fold: float
    imaging_tissue_penetration_depth_um: float
    photobleaching_rate_suppression_pct: float
    quantum_sub_shot_noise_snr_gain_db: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=QuantumEntangledPhotonMultiphotonImagingStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_quantum_entangled_photon_multiphoton_imaging(
    req: AnalyzeQuantumEntangledPhotonMultiphotonImagingRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Quantum Entangled Photon Biological Tissue Multiphoton Imaging Resolution Maximizer analysis and persist study."""
    engine = QuantumEntangledPhotonMultiphotonImagingEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = QuantumEntangledPhotonMultiphotonImagingRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        two_photon_absorption_cross_section_enhancement_fold=result.two_photon_absorption_cross_section_enhancement_fold,
        imaging_tissue_penetration_depth_um=result.imaging_tissue_penetration_depth_um,
        photobleaching_rate_suppression_pct=result.photobleaching_rate_suppression_pct,
        quantum_sub_shot_noise_snr_gain_db=result.quantum_sub_shot_noise_snr_gain_db,
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

    return QuantumEntangledPhotonMultiphotonImagingStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        two_photon_absorption_cross_section_enhancement_fold=study.two_photon_absorption_cross_section_enhancement_fold,
        imaging_tissue_penetration_depth_um=study.imaging_tissue_penetration_depth_um,
        photobleaching_rate_suppression_pct=study.photobleaching_rate_suppression_pct,
        quantum_sub_shot_noise_snr_gain_db=study.quantum_sub_shot_noise_snr_gain_db,
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


@router.get("/studies", response_model=List[QuantumEntangledPhotonMultiphotonImagingStudyResponse])
async def list_quantum_entangled_photon_multiphoton_imaging_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Quantum Entangled Photon Biological Tissue Multiphoton Imaging Resolution Maximizer studies."""
    repo = QuantumEntangledPhotonMultiphotonImagingRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=QuantumEntangledPhotonMultiphotonImagingStudyResponse)
async def get_quantum_entangled_photon_multiphoton_imaging_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Quantum Entangled Photon Biological Tissue Multiphoton Imaging Resolution Maximizer study by ID."""
    repo = QuantumEntangledPhotonMultiphotonImagingRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
