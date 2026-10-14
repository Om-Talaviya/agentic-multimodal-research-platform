"""FastAPI routes for Phase 502: Autonomous Microfluidic Acoustic Sorting & Droplet Single-Exosome Surface Tetraspanin Profiler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.acoustic_droplet_single_exosome_profiler_repo import AcousticDropletSingleExosomeProfilerRepository
from research.orchestration.acoustic_droplet_single_exosome_profiler_engine import AcousticDropletSingleExosomeProfilerEngine

router = APIRouter(prefix="/acoustic-droplet-single-exosome-profiler", tags=["acoustic-droplet-single-exosome-profiler"])


class AnalyzeAcousticDropletSingleExosomeProfilerRequest(BaseModel):
    name: str = Field(..., example="Autonomous Microfluidic Acoustic Sorting & Droplet Single-Exosome Surface Tetraspanin Profiler Run")
    target_specimen: str = Field(default="Surface Acoustic Wave (SAW) Focused Patient Plasma with CD63/CD81/CD9 Fluorophore Micro-Beads")
    analytical_modality: str = Field(default="acoustic-droplet-single-exosome")
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


class AcousticDropletSingleExosomeProfilerStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    exosome_acoustic_separation_purity_pct: float
    droplet_single_vesicle_encapsulation_lambda: float
    tetraspanin_triplet_colocalization_score: float
    low_abundant_cargo_detection_limit_fM: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=AcousticDropletSingleExosomeProfilerStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_acoustic_droplet_single_exosome_profiler(
    req: AnalyzeAcousticDropletSingleExosomeProfilerRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Microfluidic Acoustic Sorting & Droplet Single-Exosome Surface Tetraspanin Profiler analysis and persist study."""
    engine = AcousticDropletSingleExosomeProfilerEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = AcousticDropletSingleExosomeProfilerRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        exosome_acoustic_separation_purity_pct=result.exosome_acoustic_separation_purity_pct,
        droplet_single_vesicle_encapsulation_lambda=result.droplet_single_vesicle_encapsulation_lambda,
        tetraspanin_triplet_colocalization_score=result.tetraspanin_triplet_colocalization_score,
        low_abundant_cargo_detection_limit_fM=result.low_abundant_cargo_detection_limit_fM,
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

    return AcousticDropletSingleExosomeProfilerStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        exosome_acoustic_separation_purity_pct=study.exosome_acoustic_separation_purity_pct,
        droplet_single_vesicle_encapsulation_lambda=study.droplet_single_vesicle_encapsulation_lambda,
        tetraspanin_triplet_colocalization_score=study.tetraspanin_triplet_colocalization_score,
        low_abundant_cargo_detection_limit_fM=study.low_abundant_cargo_detection_limit_fM,
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


@router.get("/studies", response_model=List[AcousticDropletSingleExosomeProfilerStudyResponse])
async def list_acoustic_droplet_single_exosome_profiler_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Microfluidic Acoustic Sorting & Droplet Single-Exosome Surface Tetraspanin Profiler studies."""
    repo = AcousticDropletSingleExosomeProfilerRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=AcousticDropletSingleExosomeProfilerStudyResponse)
async def get_acoustic_droplet_single_exosome_profiler_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Microfluidic Acoustic Sorting & Droplet Single-Exosome Surface Tetraspanin Profiler study by ID."""
    repo = AcousticDropletSingleExosomeProfilerRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
