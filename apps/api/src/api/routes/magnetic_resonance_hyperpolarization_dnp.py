"""FastAPI routes for Phase 529: Autonomous Dissolution Dynamic Nuclear Polarization (DNP) Hyperpolarized Carbon-13 Flux Tracer."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.magnetic_resonance_hyperpolarization_dnp_repo import MagneticResonanceHyperpolarizationDnpRepository
from research.orchestration.magnetic_resonance_hyperpolarization_dnp_engine import MagneticResonanceHyperpolarizationDnpEngine

router = APIRouter(prefix="/magnetic-resonance-hyperpolarization-dnp", tags=["magnetic-resonance-hyperpolarization-dnp"])


class AnalyzeMagneticResonanceHyperpolarizationDnpRequest(BaseModel):
    name: str = Field(..., example="Autonomous Dissolution Dynamic Nuclear Polarization (DNP) Hyperpolarized Carbon-13 Flux Tracer Run")
    target_specimen: str = Field(default="Hyperpolarized [1-13C] Pyruvate with Trityl Radical OX063 Polarized at 1.4K and 5T")
    analytical_modality: str = Field(default="dnp-hyperpolarized-nmr-flux")
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


class MagneticResonanceHyperpolarizationDnpStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    carbon_13_nuclear_polarization_pct: float
    in_vivo_t1_relaxation_time_s: float
    pyruvate_to_lactate_apparent_flux_rate_k_pl: float
    spectroscopic_snr_enhancement_factor: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=MagneticResonanceHyperpolarizationDnpStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_magnetic_resonance_hyperpolarization_dnp(
    req: AnalyzeMagneticResonanceHyperpolarizationDnpRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Dissolution Dynamic Nuclear Polarization (DNP) Hyperpolarized Carbon-13 Flux Tracer analysis and persist study."""
    engine = MagneticResonanceHyperpolarizationDnpEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = MagneticResonanceHyperpolarizationDnpRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        carbon_13_nuclear_polarization_pct=result.carbon_13_nuclear_polarization_pct,
        in_vivo_t1_relaxation_time_s=result.in_vivo_t1_relaxation_time_s,
        pyruvate_to_lactate_apparent_flux_rate_k_pl=result.pyruvate_to_lactate_apparent_flux_rate_k_pl,
        spectroscopic_snr_enhancement_factor=result.spectroscopic_snr_enhancement_factor,
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

    return MagneticResonanceHyperpolarizationDnpStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        carbon_13_nuclear_polarization_pct=study.carbon_13_nuclear_polarization_pct,
        in_vivo_t1_relaxation_time_s=study.in_vivo_t1_relaxation_time_s,
        pyruvate_to_lactate_apparent_flux_rate_k_pl=study.pyruvate_to_lactate_apparent_flux_rate_k_pl,
        spectroscopic_snr_enhancement_factor=study.spectroscopic_snr_enhancement_factor,
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


@router.get("/studies", response_model=List[MagneticResonanceHyperpolarizationDnpStudyResponse])
async def list_magnetic_resonance_hyperpolarization_dnp_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Dissolution Dynamic Nuclear Polarization (DNP) Hyperpolarized Carbon-13 Flux Tracer studies."""
    repo = MagneticResonanceHyperpolarizationDnpRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=MagneticResonanceHyperpolarizationDnpStudyResponse)
async def get_magnetic_resonance_hyperpolarization_dnp_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Dissolution Dynamic Nuclear Polarization (DNP) Hyperpolarized Carbon-13 Flux Tracer study by ID."""
    repo = MagneticResonanceHyperpolarizationDnpRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
