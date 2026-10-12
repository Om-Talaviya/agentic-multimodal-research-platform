"""FastAPI routes for Phase 417: Autonomous Solid-State Silicon Nitride Nanopore Single-Molecule Protein Translocation Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.solid_state_nanopore_single_molecule_sensing_repo import SolidStateNanoporeSensingRepository
from research.orchestration.solid_state_nanopore_single_molecule_sensing_engine import SolidStateNanoporeSensingEngine

router = APIRouter(prefix="/solid-state-nanopore-sensing", tags=["solid-state-nanopore-sensing"])


class AnalyzeSolidStateNanoporeSensingRequest(BaseModel):
    name: str = Field(..., example="Autonomous Solid-State Silicon Nitride Nanopore Single-Molecule Protein Translocation Engine Run")
    target_specimen: str = Field(default="Conformationally Stretched Native Protein Translocation Through Sub-5nm SiNx Nanopore")
    analytical_modality: str = Field(default="solid-state-nanopore")
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


class SolidStateNanoporeSensingStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    translocation_dwell_time_us: float
    fractional_current_blockade_ratio: float
    nanopore_diameter_nm: float
    capture_frequency_events_per_s: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=SolidStateNanoporeSensingStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_solid_state_nanopore_single_molecule_sensing(
    req: AnalyzeSolidStateNanoporeSensingRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Solid-State Silicon Nitride Nanopore Single-Molecule Protein Translocation Engine analysis and persist study."""
    engine = SolidStateNanoporeSensingEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SolidStateNanoporeSensingRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        translocation_dwell_time_us=result.translocation_dwell_time_us,
        fractional_current_blockade_ratio=result.fractional_current_blockade_ratio,
        nanopore_diameter_nm=result.nanopore_diameter_nm,
        capture_frequency_events_per_s=result.capture_frequency_events_per_s,
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

    return SolidStateNanoporeSensingStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        translocation_dwell_time_us=study.translocation_dwell_time_us,
        fractional_current_blockade_ratio=study.fractional_current_blockade_ratio,
        nanopore_diameter_nm=study.nanopore_diameter_nm,
        capture_frequency_events_per_s=study.capture_frequency_events_per_s,
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


@router.get("/studies", response_model=List[SolidStateNanoporeSensingStudyResponse])
async def list_solid_state_nanopore_single_molecule_sensing_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Solid-State Silicon Nitride Nanopore Single-Molecule Protein Translocation Engine studies."""
    repo = SolidStateNanoporeSensingRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SolidStateNanoporeSensingStudyResponse)
async def get_solid_state_nanopore_single_molecule_sensing_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Solid-State Silicon Nitride Nanopore Single-Molecule Protein Translocation Engine study by ID."""
    repo = SolidStateNanoporeSensingRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
