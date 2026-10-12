"""FastAPI routes for Phase 415: Autonomous Epitranscriptomic Direct RNA Nanopore Pseudouridine (Psi) & m6A Stoichiometry Profiler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.direct_rna_nanopore_pseudouridine_repo import DirectRnaNanoporePseudouridineRepository
from research.orchestration.direct_rna_nanopore_pseudouridine_engine import DirectRnaNanoporePseudouridineEngine

router = APIRouter(prefix="/direct-rna-nanopore-pseudouridine", tags=["direct-rna-nanopore-pseudouridine"])


class AnalyzeDirectRnaNanoporePseudouridineRequest(BaseModel):
    name: str = Field(..., example="Autonomous Epitranscriptomic Direct RNA Nanopore Pseudouridine (Psi) & m6A Stoichiometry Profiler Run")
    target_specimen: str = Field(default="Cellular Poly(A)+ Native mRNA Transcriptome")
    analytical_modality: str = Field(default="direct-rna-nanopore")
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


class DirectRnaNanoporePseudouridineStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    pseudouridine_stoichiometry_ratio: float
    nanopore_dwell_time_shift_ms: float
    ionic_current_deviation_pA: float
    m6a_modification_frequency: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=DirectRnaNanoporePseudouridineStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_direct_rna_nanopore_pseudouridine(
    req: AnalyzeDirectRnaNanoporePseudouridineRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Epitranscriptomic Direct RNA Nanopore Pseudouridine (Psi) & m6A Stoichiometry Profiler analysis and persist study."""
    engine = DirectRnaNanoporePseudouridineEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = DirectRnaNanoporePseudouridineRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        pseudouridine_stoichiometry_ratio=result.pseudouridine_stoichiometry_ratio,
        nanopore_dwell_time_shift_ms=result.nanopore_dwell_time_shift_ms,
        ionic_current_deviation_pA=result.ionic_current_deviation_pA,
        m6a_modification_frequency=result.m6a_modification_frequency,
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

    return DirectRnaNanoporePseudouridineStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        pseudouridine_stoichiometry_ratio=study.pseudouridine_stoichiometry_ratio,
        nanopore_dwell_time_shift_ms=study.nanopore_dwell_time_shift_ms,
        ionic_current_deviation_pA=study.ionic_current_deviation_pA,
        m6a_modification_frequency=study.m6a_modification_frequency,
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


@router.get("/studies", response_model=List[DirectRnaNanoporePseudouridineStudyResponse])
async def list_direct_rna_nanopore_pseudouridine_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Epitranscriptomic Direct RNA Nanopore Pseudouridine (Psi) & m6A Stoichiometry Profiler studies."""
    repo = DirectRnaNanoporePseudouridineRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=DirectRnaNanoporePseudouridineStudyResponse)
async def get_direct_rna_nanopore_pseudouridine_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Epitranscriptomic Direct RNA Nanopore Pseudouridine (Psi) & m6A Stoichiometry Profiler study by ID."""
    repo = DirectRnaNanoporePseudouridineRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
