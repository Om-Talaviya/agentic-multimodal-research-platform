"""FastAPI routes for Phase 525: Autonomous Engineered Cas12a Direct RNA Single-Nucleotide Variant Diagnostic Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.crispr_cas12a_direct_rna_targeting_diagnostics_repo import CrisprCas12aDirectRnaTargetingDiagnosticsRepository
from research.orchestration.crispr_cas12a_direct_rna_targeting_diagnostics_engine import CrisprCas12aDirectRnaTargetingDiagnosticsEngine

router = APIRouter(prefix="/crispr-cas12a-direct-rna-targeting-diagnostics", tags=["crispr-cas12a-direct-rna-targeting-diagnostics"])


class AnalyzeCrisprCas12aDirectRnaTargetingDiagnosticsRequest(BaseModel):
    name: str = Field(..., example="Autonomous Engineered Cas12a Direct RNA Single-Nucleotide Variant Diagnostic Engine Run")
    target_specimen: str = Field(default="Engineered Dual-Domain Acidaminococcus sp. Cas12a Variant bound to Synthetic SARS-CoV-3 RNA Target")
    analytical_modality: str = Field(default="cas12a-direct-rna-cleavage")
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


class CrisprCas12aDirectRnaTargetingDiagnosticsStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    collateral_ssdna_probe_turnover_rate_s_inv: float
    single_nucleotide_variant_specificity_ratio: float
    limit_of_detection_attomolar_aM: float
    isothermal_reaction_kinetic_delay_time_min: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=CrisprCas12aDirectRnaTargetingDiagnosticsStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_crispr_cas12a_direct_rna_targeting_diagnostics(
    req: AnalyzeCrisprCas12aDirectRnaTargetingDiagnosticsRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Engineered Cas12a Direct RNA Single-Nucleotide Variant Diagnostic Engine analysis and persist study."""
    engine = CrisprCas12aDirectRnaTargetingDiagnosticsEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = CrisprCas12aDirectRnaTargetingDiagnosticsRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        collateral_ssdna_probe_turnover_rate_s_inv=result.collateral_ssdna_probe_turnover_rate_s_inv,
        single_nucleotide_variant_specificity_ratio=result.single_nucleotide_variant_specificity_ratio,
        limit_of_detection_attomolar_aM=result.limit_of_detection_attomolar_aM,
        isothermal_reaction_kinetic_delay_time_min=result.isothermal_reaction_kinetic_delay_time_min,
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

    return CrisprCas12aDirectRnaTargetingDiagnosticsStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        collateral_ssdna_probe_turnover_rate_s_inv=study.collateral_ssdna_probe_turnover_rate_s_inv,
        single_nucleotide_variant_specificity_ratio=study.single_nucleotide_variant_specificity_ratio,
        limit_of_detection_attomolar_aM=study.limit_of_detection_attomolar_aM,
        isothermal_reaction_kinetic_delay_time_min=study.isothermal_reaction_kinetic_delay_time_min,
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


@router.get("/studies", response_model=List[CrisprCas12aDirectRnaTargetingDiagnosticsStudyResponse])
async def list_crispr_cas12a_direct_rna_targeting_diagnostics_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Engineered Cas12a Direct RNA Single-Nucleotide Variant Diagnostic Engine studies."""
    repo = CrisprCas12aDirectRnaTargetingDiagnosticsRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=CrisprCas12aDirectRnaTargetingDiagnosticsStudyResponse)
async def get_crispr_cas12a_direct_rna_targeting_diagnostics_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Engineered Cas12a Direct RNA Single-Nucleotide Variant Diagnostic Engine study by ID."""
    repo = CrisprCas12aDirectRnaTargetingDiagnosticsRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
