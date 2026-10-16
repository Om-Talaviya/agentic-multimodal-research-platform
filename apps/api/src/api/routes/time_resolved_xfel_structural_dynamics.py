"""FastAPI routes for Phase 557: Autonomous Time-Resolved Femtosecond X-ray Free-Electron Laser (XFEL) Macromolecular Structural Dynamics Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.time_resolved_xfel_structural_dynamics_repo import TimeResolvedXfelStructuralDynamicsRepository
from research.orchestration.time_resolved_xfel_structural_dynamics_engine import TimeResolvedXfelStructuralDynamicsEngine

router = APIRouter(prefix="/time-resolved-xfel-structural-dynamics", tags=["time-resolved-xfel-structural-dynamics"])


class AnalyzeTimeResolvedXfelStructuralDynamicsRequest(BaseModel):
    name: str = Field(..., example="Autonomous Time-Resolved Femtosecond X-ray Free-Electron Laser (XFEL) Macromolecular Structural Dynamics Engine Run")
    target_specimen: str = Field(default="Photoactive Yellow Protein (PYP) Microcrystals probed by 10-fs X-ray Pulses at LCLS-II after 450nm Laser Photolysis")
    analytical_modality: str = Field(default="time-resolved-xfel-dynamics")
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


class TimeResolvedXfelStructuralDynamicsStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    femtosecond_temporal_resolution_fs: float
    chromophore_trans_to_cis_isomerization_time_ps: float
    difference_electron_density_signal_snr: float
    serial_femtosecond_crystallography_resolution_a: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=TimeResolvedXfelStructuralDynamicsStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_time_resolved_xfel_structural_dynamics(
    req: AnalyzeTimeResolvedXfelStructuralDynamicsRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Time-Resolved Femtosecond X-ray Free-Electron Laser (XFEL) Macromolecular Structural Dynamics Engine analysis and persist study."""
    engine = TimeResolvedXfelStructuralDynamicsEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = TimeResolvedXfelStructuralDynamicsRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        femtosecond_temporal_resolution_fs=result.femtosecond_temporal_resolution_fs,
        chromophore_trans_to_cis_isomerization_time_ps=result.chromophore_trans_to_cis_isomerization_time_ps,
        difference_electron_density_signal_snr=result.difference_electron_density_signal_snr,
        serial_femtosecond_crystallography_resolution_a=result.serial_femtosecond_crystallography_resolution_a,
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

    return TimeResolvedXfelStructuralDynamicsStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        femtosecond_temporal_resolution_fs=study.femtosecond_temporal_resolution_fs,
        chromophore_trans_to_cis_isomerization_time_ps=study.chromophore_trans_to_cis_isomerization_time_ps,
        difference_electron_density_signal_snr=study.difference_electron_density_signal_snr,
        serial_femtosecond_crystallography_resolution_a=study.serial_femtosecond_crystallography_resolution_a,
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


@router.get("/studies", response_model=List[TimeResolvedXfelStructuralDynamicsStudyResponse])
async def list_time_resolved_xfel_structural_dynamics_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Time-Resolved Femtosecond X-ray Free-Electron Laser (XFEL) Macromolecular Structural Dynamics Engine studies."""
    repo = TimeResolvedXfelStructuralDynamicsRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=TimeResolvedXfelStructuralDynamicsStudyResponse)
async def get_time_resolved_xfel_structural_dynamics_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Time-Resolved Femtosecond X-ray Free-Electron Laser (XFEL) Macromolecular Structural Dynamics Engine study by ID."""
    repo = TimeResolvedXfelStructuralDynamicsRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
