"""FastAPI routes for Phase 478: Autonomous Solid-State Nanopore DNA Methylation Direct Ionic Current Discrimination Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.nanopore_dna_methylation_discrimination_repo import NanoporeDnaMethylationDiscriminationRepository
from research.orchestration.nanopore_dna_methylation_discrimination_engine import NanoporeDnaMethylationDiscriminationEngine

router = APIRouter(prefix="/nanopore-dna-methylation-discrimination", tags=["nanopore-dna-methylation-discrimination"])


class AnalyzeNanoporeDnaMethylationDiscriminationRequest(BaseModel):
    name: str = Field(..., example="Autonomous Solid-State Nanopore DNA Methylation Direct Ionic Current Discrimination Engine Run")
    target_specimen: str = Field(default="Sub-2nm Si3N4 Nanopore Translocating Native Synthetic 5mC / 5hmC Epigenetic DNA Duplexes")
    analytical_modality: str = Field(default="nanopore-methylation-discrimination")
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


class NanoporeDnaMethylationDiscriminationStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    fractional_current_blockade_ratio: float
    epigenetic_base_dwell_time_us: float
    five_mc_vs_unmethylated_snr_db: float
    single_base_resolution_confidence: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=NanoporeDnaMethylationDiscriminationStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_nanopore_dna_methylation_discrimination(
    req: AnalyzeNanoporeDnaMethylationDiscriminationRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Solid-State Nanopore DNA Methylation Direct Ionic Current Discrimination Engine analysis and persist study."""
    engine = NanoporeDnaMethylationDiscriminationEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = NanoporeDnaMethylationDiscriminationRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        fractional_current_blockade_ratio=result.fractional_current_blockade_ratio,
        epigenetic_base_dwell_time_us=result.epigenetic_base_dwell_time_us,
        five_mc_vs_unmethylated_snr_db=result.five_mc_vs_unmethylated_snr_db,
        single_base_resolution_confidence=result.single_base_resolution_confidence,
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

    return NanoporeDnaMethylationDiscriminationStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        fractional_current_blockade_ratio=study.fractional_current_blockade_ratio,
        epigenetic_base_dwell_time_us=study.epigenetic_base_dwell_time_us,
        five_mc_vs_unmethylated_snr_db=study.five_mc_vs_unmethylated_snr_db,
        single_base_resolution_confidence=study.single_base_resolution_confidence,
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


@router.get("/studies", response_model=List[NanoporeDnaMethylationDiscriminationStudyResponse])
async def list_nanopore_dna_methylation_discrimination_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Solid-State Nanopore DNA Methylation Direct Ionic Current Discrimination Engine studies."""
    repo = NanoporeDnaMethylationDiscriminationRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=NanoporeDnaMethylationDiscriminationStudyResponse)
async def get_nanopore_dna_methylation_discrimination_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Solid-State Nanopore DNA Methylation Direct Ionic Current Discrimination Engine study by ID."""
    repo = NanoporeDnaMethylationDiscriminationRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
