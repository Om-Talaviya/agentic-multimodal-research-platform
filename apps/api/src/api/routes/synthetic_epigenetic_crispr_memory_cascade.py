"""FastAPI routes for Phase 535: Autonomous Multi-Tier Synthetic Epigenetic CRISPR Reversible Silencing Transcriptional Memory Cascade."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.synthetic_epigenetic_crispr_memory_cascade_repo import SyntheticEpigeneticCrisprMemoryCascadeRepository
from research.orchestration.synthetic_epigenetic_crispr_memory_cascade_engine import SyntheticEpigeneticCrisprMemoryCascadeEngine

router = APIRouter(prefix="/synthetic-epigenetic-crispr-memory-cascade", tags=["synthetic-epigenetic-crispr-memory-cascade"])


class AnalyzeSyntheticEpigeneticCrisprMemoryCascadeRequest(BaseModel):
    name: str = Field(..., example="Autonomous Multi-Tier Synthetic Epigenetic CRISPR Reversible Silencing Transcriptional Memory Cascade Run")
    target_specimen: str = Field(default="Engineered dCas9-KRAB-MeCP2 & dCas9-TET1 Autocatalytic Feedback Toggle in Human iPSCs")
    analytical_modality: str = Field(default="crispr-epigenetic-memory-cascade")
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


class SyntheticEpigeneticCrisprMemoryCascadeStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    transcriptional_repression_half_life_days: float
    h3k9me3_deposition_spreading_kb: float
    epigenetic_memory_heritability_generations: float
    reversible_reactivation_efficiency_pct: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=SyntheticEpigeneticCrisprMemoryCascadeStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_synthetic_epigenetic_crispr_memory_cascade(
    req: AnalyzeSyntheticEpigeneticCrisprMemoryCascadeRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Multi-Tier Synthetic Epigenetic CRISPR Reversible Silencing Transcriptional Memory Cascade analysis and persist study."""
    engine = SyntheticEpigeneticCrisprMemoryCascadeEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SyntheticEpigeneticCrisprMemoryCascadeRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        transcriptional_repression_half_life_days=result.transcriptional_repression_half_life_days,
        h3k9me3_deposition_spreading_kb=result.h3k9me3_deposition_spreading_kb,
        epigenetic_memory_heritability_generations=result.epigenetic_memory_heritability_generations,
        reversible_reactivation_efficiency_pct=result.reversible_reactivation_efficiency_pct,
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

    return SyntheticEpigeneticCrisprMemoryCascadeStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        transcriptional_repression_half_life_days=study.transcriptional_repression_half_life_days,
        h3k9me3_deposition_spreading_kb=study.h3k9me3_deposition_spreading_kb,
        epigenetic_memory_heritability_generations=study.epigenetic_memory_heritability_generations,
        reversible_reactivation_efficiency_pct=study.reversible_reactivation_efficiency_pct,
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


@router.get("/studies", response_model=List[SyntheticEpigeneticCrisprMemoryCascadeStudyResponse])
async def list_synthetic_epigenetic_crispr_memory_cascade_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Multi-Tier Synthetic Epigenetic CRISPR Reversible Silencing Transcriptional Memory Cascade studies."""
    repo = SyntheticEpigeneticCrisprMemoryCascadeRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SyntheticEpigeneticCrisprMemoryCascadeStudyResponse)
async def get_synthetic_epigenetic_crispr_memory_cascade_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Multi-Tier Synthetic Epigenetic CRISPR Reversible Silencing Transcriptional Memory Cascade study by ID."""
    repo = SyntheticEpigeneticCrisprMemoryCascadeRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
