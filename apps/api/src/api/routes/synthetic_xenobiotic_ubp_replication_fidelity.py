"""FastAPI routes for Phase 562: Autonomous Synthetic Xenobiotic Unnatural Base Pair (UBP: dNaM-d5SICS) DNA Replication Fidelity Forecaster."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.synthetic_xenobiotic_ubp_replication_fidelity_repo import SyntheticXenobioticUbpReplicationFidelityRepository
from research.orchestration.synthetic_xenobiotic_ubp_replication_fidelity_engine import SyntheticXenobioticUbpReplicationFidelityEngine

router = APIRouter(prefix="/synthetic-xenobiotic-ubp-replication-fidelity", tags=["synthetic-xenobiotic-ubp-replication-fidelity"])


class AnalyzeSyntheticXenobioticUbpReplicationFidelityRequest(BaseModel):
    name: str = Field(..., example="Autonomous Synthetic Xenobiotic Unnatural Base Pair (UBP: dNaM-d5SICS) DNA Replication Fidelity Forecaster Run")
    target_specimen: str = Field(default="Engineered Semi-Synthetic Organism E. coli with dNaM-d5SICS 6-Letter Genetic Alphabet and Nucleoside Triphosphate Transporter")
    analytical_modality: str = Field(default="xenobiotic-unnatural-base-pair")
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


class SyntheticXenobioticUbpReplicationFidelityStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    six_letter_replication_fidelity_pct_per_doubling: float
    ubp_retention_half_life_generations: float
    unnatural_triphosphate_uptake_flux_pmol_min: float
    polymerase_bypass_insertion_efficiency_kcat_km: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=SyntheticXenobioticUbpReplicationFidelityStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_synthetic_xenobiotic_ubp_replication_fidelity(
    req: AnalyzeSyntheticXenobioticUbpReplicationFidelityRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Synthetic Xenobiotic Unnatural Base Pair (UBP: dNaM-d5SICS) DNA Replication Fidelity Forecaster analysis and persist study."""
    engine = SyntheticXenobioticUbpReplicationFidelityEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SyntheticXenobioticUbpReplicationFidelityRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        six_letter_replication_fidelity_pct_per_doubling=result.six_letter_replication_fidelity_pct_per_doubling,
        ubp_retention_half_life_generations=result.ubp_retention_half_life_generations,
        unnatural_triphosphate_uptake_flux_pmol_min=result.unnatural_triphosphate_uptake_flux_pmol_min,
        polymerase_bypass_insertion_efficiency_kcat_km=result.polymerase_bypass_insertion_efficiency_kcat_km,
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

    return SyntheticXenobioticUbpReplicationFidelityStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        six_letter_replication_fidelity_pct_per_doubling=study.six_letter_replication_fidelity_pct_per_doubling,
        ubp_retention_half_life_generations=study.ubp_retention_half_life_generations,
        unnatural_triphosphate_uptake_flux_pmol_min=study.unnatural_triphosphate_uptake_flux_pmol_min,
        polymerase_bypass_insertion_efficiency_kcat_km=study.polymerase_bypass_insertion_efficiency_kcat_km,
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


@router.get("/studies", response_model=List[SyntheticXenobioticUbpReplicationFidelityStudyResponse])
async def list_synthetic_xenobiotic_ubp_replication_fidelity_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Synthetic Xenobiotic Unnatural Base Pair (UBP: dNaM-d5SICS) DNA Replication Fidelity Forecaster studies."""
    repo = SyntheticXenobioticUbpReplicationFidelityRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SyntheticXenobioticUbpReplicationFidelityStudyResponse)
async def get_synthetic_xenobiotic_ubp_replication_fidelity_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Synthetic Xenobiotic Unnatural Base Pair (UBP: dNaM-d5SICS) DNA Replication Fidelity Forecaster study by ID."""
    repo = SyntheticXenobioticUbpReplicationFidelityRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
