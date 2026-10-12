"""FastAPI routes for Phase 441: Autonomous Fenna-Matthews-Olson (FMO) Complex Quantum Exciton Energy Transfer & Coherence Modeler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.photosystem_quantum_coherence_exciton_fmo_repo import PhotosystemQuantumCoherenceRepository
from research.orchestration.photosystem_quantum_coherence_exciton_fmo_engine import PhotosystemQuantumCoherenceEngine

router = APIRouter(prefix="/photosystem-quantum-coherence", tags=["photosystem-quantum-coherence"])


class AnalyzePhotosystemQuantumCoherenceRequest(BaseModel):
    name: str = Field(..., example="Autonomous Fenna-Matthews-Olson (FMO) Complex Quantum Exciton Energy Transfer & Coherence Modeler Run")
    target_specimen: str = Field(default="Green Sulfur Bacteria Chlorobium tepidum FMO Bacteriochlorophyll Trimer")
    analytical_modality: str = Field(default="quantum-exciton-fmo")
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


class PhotosystemQuantumCoherenceStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    exciton_transfer_efficiency_ratio: float
    quantum_coherence_lifetime_fs: float
    site_energy_disorder_cm_inv: float
    sink_bchl_trapping_rate_ps_inv: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=PhotosystemQuantumCoherenceStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_photosystem_quantum_coherence_exciton_fmo(
    req: AnalyzePhotosystemQuantumCoherenceRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Fenna-Matthews-Olson (FMO) Complex Quantum Exciton Energy Transfer & Coherence Modeler analysis and persist study."""
    engine = PhotosystemQuantumCoherenceEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = PhotosystemQuantumCoherenceRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        exciton_transfer_efficiency_ratio=result.exciton_transfer_efficiency_ratio,
        quantum_coherence_lifetime_fs=result.quantum_coherence_lifetime_fs,
        site_energy_disorder_cm_inv=result.site_energy_disorder_cm_inv,
        sink_bchl_trapping_rate_ps_inv=result.sink_bchl_trapping_rate_ps_inv,
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

    return PhotosystemQuantumCoherenceStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        exciton_transfer_efficiency_ratio=study.exciton_transfer_efficiency_ratio,
        quantum_coherence_lifetime_fs=study.quantum_coherence_lifetime_fs,
        site_energy_disorder_cm_inv=study.site_energy_disorder_cm_inv,
        sink_bchl_trapping_rate_ps_inv=study.sink_bchl_trapping_rate_ps_inv,
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


@router.get("/studies", response_model=List[PhotosystemQuantumCoherenceStudyResponse])
async def list_photosystem_quantum_coherence_exciton_fmo_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Fenna-Matthews-Olson (FMO) Complex Quantum Exciton Energy Transfer & Coherence Modeler studies."""
    repo = PhotosystemQuantumCoherenceRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=PhotosystemQuantumCoherenceStudyResponse)
async def get_photosystem_quantum_coherence_exciton_fmo_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Fenna-Matthews-Olson (FMO) Complex Quantum Exciton Energy Transfer & Coherence Modeler study by ID."""
    repo = PhotosystemQuantumCoherenceRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
