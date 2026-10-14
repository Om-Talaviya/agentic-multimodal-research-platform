"""FastAPI routes for Phase 503: Autonomous Synthetic Protocellular Compartment Membraneless Coacervate-GUV Hybrid Bionanoreactor."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.coacervate_guv_hybrid_bionanoreactor_repo import CoacervateGuvHybridBionanoreactorRepository
from research.orchestration.coacervate_guv_hybrid_bionanoreactor_engine import CoacervateGuvHybridBionanoreactorEngine

router = APIRouter(prefix="/coacervate-guv-hybrid-bionanoreactor", tags=["coacervate-guv-hybrid-bionanoreactor"])


class AnalyzeCoacervateGuvHybridBionanoreactorRequest(BaseModel):
    name: str = Field(..., example="Autonomous Synthetic Protocellular Compartment Membraneless Coacervate-GUV Hybrid Bionanoreactor Run")
    target_specimen: str = Field(default="Liquid-Liquid Phase Separated Polylysine-ATP Coacervates Encapsulated within POPC/Cholesterol Bilayer GUVs")
    analytical_modality: str = Field(default="coacervate-guv-hybrid-reactor")
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


class CoacervateGuvHybridBionanoreactorStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    enzyme_partition_coefficient_k_partition: float
    internal_substrate_conversion_flux_uM_per_s: float
    membrane_selective_permeation_pore_cutoff_kDa: float
    coacervate_droplet_stability_retention_days: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=CoacervateGuvHybridBionanoreactorStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_coacervate_guv_hybrid_bionanoreactor(
    req: AnalyzeCoacervateGuvHybridBionanoreactorRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Synthetic Protocellular Compartment Membraneless Coacervate-GUV Hybrid Bionanoreactor analysis and persist study."""
    engine = CoacervateGuvHybridBionanoreactorEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = CoacervateGuvHybridBionanoreactorRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        enzyme_partition_coefficient_k_partition=result.enzyme_partition_coefficient_k_partition,
        internal_substrate_conversion_flux_uM_per_s=result.internal_substrate_conversion_flux_uM_per_s,
        membrane_selective_permeation_pore_cutoff_kDa=result.membrane_selective_permeation_pore_cutoff_kDa,
        coacervate_droplet_stability_retention_days=result.coacervate_droplet_stability_retention_days,
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

    return CoacervateGuvHybridBionanoreactorStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        enzyme_partition_coefficient_k_partition=study.enzyme_partition_coefficient_k_partition,
        internal_substrate_conversion_flux_uM_per_s=study.internal_substrate_conversion_flux_uM_per_s,
        membrane_selective_permeation_pore_cutoff_kDa=study.membrane_selective_permeation_pore_cutoff_kDa,
        coacervate_droplet_stability_retention_days=study.coacervate_droplet_stability_retention_days,
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


@router.get("/studies", response_model=List[CoacervateGuvHybridBionanoreactorStudyResponse])
async def list_coacervate_guv_hybrid_bionanoreactor_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Synthetic Protocellular Compartment Membraneless Coacervate-GUV Hybrid Bionanoreactor studies."""
    repo = CoacervateGuvHybridBionanoreactorRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=CoacervateGuvHybridBionanoreactorStudyResponse)
async def get_coacervate_guv_hybrid_bionanoreactor_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Synthetic Protocellular Compartment Membraneless Coacervate-GUV Hybrid Bionanoreactor study by ID."""
    repo = CoacervateGuvHybridBionanoreactorRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
