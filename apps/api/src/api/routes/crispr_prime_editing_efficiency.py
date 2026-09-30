"""FastAPI routes for Phase 404: Deep Multi-Task CRISPR Prime Editing RT-Template Efficiency Forecaster Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.crispr_prime_editing_efficiency_repo import CrisprPrimeEditingEfficiencyRepository
from research.orchestration.crispr_prime_editing_efficiency_engine import CrisprPrimeEditingEfficiencyEngine

router = APIRouter(prefix="/crispr-prime-editing-efficiency", tags=["crispr-prime-editing-efficiency"])


class AnalyzeCrisprPrimeEditingEfficiencyRequest(BaseModel):
    name: str = Field(..., example="Autonomous Deep Multi-Task CRISPR Prime Editing RT-Template Efficiency Forecaster Run")
    target_specimen: str = Field(default="Human Patient Cohort Sample")
    analytical_modality: str = Field(default="crispr-prime-editing-efficiency")
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


class CrisprPrimeEditingEfficiencyStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    prime_editing_intended_insertion_efficiency_pct: float
    indel_byproduct_purity_ratio_intended_to_indel: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=CrisprPrimeEditingEfficiencyStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_crispr_prime_editing_efficiency(
    req: AnalyzeCrisprPrimeEditingEfficiencyRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Deep Multi-Task CRISPR Prime Editing RT-Template Efficiency Forecaster analysis and persist study record."""
    engine = CrisprPrimeEditingEfficiencyEngine()
    analysis = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = CrisprPrimeEditingEfficiencyRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=analysis.target_specimen,
        analytical_modality=analysis.analytical_modality,
        prime_editing_intended_insertion_efficiency_pct=getattr(analysis, "prime_editing_intended_insertion_efficiency_pct"),
        indel_byproduct_purity_ratio_intended_to_indel=getattr(analysis, "indel_byproduct_purity_ratio_intended_to_indel"),
        confidence_score=analysis.confidence_score,
        status="completed",
        summary_report=analysis.summary_report,
    )

    for it in analysis.item_profiles:
        await repo.add_item_profile(
            study_id=study.id,
            item_name=it.item_name,
            profile_category=it.profile_category,
            quantitative_value=it.quantitative_value,
            log2_fold_change=it.log2_fold_change,
            significance_score=it.significance_score,
        )

    for tr in analysis.metric_traces:
        await repo.add_metric_trace(
            study_id=study.id,
            metric_dimension=tr.metric_dimension,
            observed_value=tr.observed_value,
            z_score=tr.z_score,
            p_value=tr.p_value,
        )

    return CrisprPrimeEditingEfficiencyStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        prime_editing_intended_insertion_efficiency_pct=getattr(study, "prime_editing_intended_insertion_efficiency_pct"),
        indel_byproduct_purity_ratio_intended_to_indel=getattr(study, "indel_byproduct_purity_ratio_intended_to_indel"),
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
            ) for it in analysis.item_profiles
        ],
        metric_traces=[
            MetricTraceResponse(
                metric_dimension=tr.metric_dimension,
                observed_value=tr.observed_value,
                z_score=tr.z_score,
                p_value=tr.p_value,
            ) for tr in analysis.metric_traces
        ],
    )


@router.get("/studies", response_model=List[CrisprPrimeEditingEfficiencyStudyResponse])
async def list_crispr_prime_editing_efficiency_studies(
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List historical Deep Multi-Task CRISPR Prime Editing RT-Template Efficiency Forecaster studies."""
    repo = CrisprPrimeEditingEfficiencyRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        CrisprPrimeEditingEfficiencyStudyResponse(
            id=s.id,
            name=s.name,
            target_specimen=s.target_specimen,
            analytical_modality=s.analytical_modality,
            prime_editing_intended_insertion_efficiency_pct=getattr(s, "prime_editing_intended_insertion_efficiency_pct"),
            indel_byproduct_purity_ratio_intended_to_indel=getattr(s, "indel_byproduct_purity_ratio_intended_to_indel"),
            confidence_score=s.confidence_score,
            status=s.status,
            summary_report=s.summary_report,
            item_profiles=[],
            metric_traces=[],
        ) for s in studies
    ]


@router.get("/studies/{study_id}", response_model=CrisprPrimeEditingEfficiencyStudyResponse)
async def get_crispr_prime_editing_efficiency_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve details for a single Deep Multi-Task CRISPR Prime Editing RT-Template Efficiency Forecaster study."""
    repo = CrisprPrimeEditingEfficiencyRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")
    return CrisprPrimeEditingEfficiencyStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        prime_editing_intended_insertion_efficiency_pct=getattr(study, "prime_editing_intended_insertion_efficiency_pct"),
        indel_byproduct_purity_ratio_intended_to_indel=getattr(study, "indel_byproduct_purity_ratio_intended_to_indel"),
        confidence_score=study.confidence_score,
        status=study.status,
        summary_report=study.summary_report,
        item_profiles=[],
        metric_traces=[],
    )
