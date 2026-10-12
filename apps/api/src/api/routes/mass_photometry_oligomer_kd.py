"""FastAPI routes for Phase 426: Autonomous Mass Photometry Macromolecular Oligomeric Mass Distribution & Dissociation Constant (KD) Estimator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.mass_photometry_oligomer_kd_repo import MassPhotometryOligomerKdRepository
from research.orchestration.mass_photometry_oligomer_kd_engine import MassPhotometryOligomerKdEngine

router = APIRouter(prefix="/mass-photometry-oligomer-kd", tags=["mass-photometry-oligomer-kd"])


class AnalyzeMassPhotometryOligomerKdRequest(BaseModel):
    name: str = Field(..., example="Autonomous Mass Photometry Macromolecular Oligomeric Mass Distribution & Dissociation Constant (KD) Estimator Run")
    target_specimen: str = Field(default="Native Macromolecular Assembly on Glass Coverslip Surface")
    analytical_modality: str = Field(default="mass-photometry-kd")
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


class MassPhotometryOligomerKdStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    molecular_mass_kda: float
    equilibrium_dissociation_constant_nM: float
    dimer_to_monomer_peak_ratio: float
    contrast_interferometry_snr: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=MassPhotometryOligomerKdStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_mass_photometry_oligomer_kd(
    req: AnalyzeMassPhotometryOligomerKdRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Mass Photometry Macromolecular Oligomeric Mass Distribution & Dissociation Constant (KD) Estimator analysis and persist study."""
    engine = MassPhotometryOligomerKdEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = MassPhotometryOligomerKdRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        molecular_mass_kda=result.molecular_mass_kda,
        equilibrium_dissociation_constant_nM=result.equilibrium_dissociation_constant_nM,
        dimer_to_monomer_peak_ratio=result.dimer_to_monomer_peak_ratio,
        contrast_interferometry_snr=result.contrast_interferometry_snr,
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

    return MassPhotometryOligomerKdStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        molecular_mass_kda=study.molecular_mass_kda,
        equilibrium_dissociation_constant_nM=study.equilibrium_dissociation_constant_nM,
        dimer_to_monomer_peak_ratio=study.dimer_to_monomer_peak_ratio,
        contrast_interferometry_snr=study.contrast_interferometry_snr,
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


@router.get("/studies", response_model=List[MassPhotometryOligomerKdStudyResponse])
async def list_mass_photometry_oligomer_kd_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Mass Photometry Macromolecular Oligomeric Mass Distribution & Dissociation Constant (KD) Estimator studies."""
    repo = MassPhotometryOligomerKdRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=MassPhotometryOligomerKdStudyResponse)
async def get_mass_photometry_oligomer_kd_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Mass Photometry Macromolecular Oligomeric Mass Distribution & Dissociation Constant (KD) Estimator study by ID."""
    repo = MassPhotometryOligomerKdRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
