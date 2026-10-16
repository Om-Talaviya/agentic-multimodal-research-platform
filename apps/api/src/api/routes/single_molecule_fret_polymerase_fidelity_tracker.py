"""FastAPI route for Phase 576: Autonomous Single-Molecule smFRET High-Fidelity DNA Polymerase Mismatch Proofreading & Exonuclease Kinetic Tracker."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.single_molecule_fret_polymerase_fidelity_tracker_repo import SingleMoleculeFretPolymeraseFidelityTrackerRepository
from research.orchestration.single_molecule_fret_polymerase_fidelity_tracker_engine import SingleMoleculeFretPolymeraseFidelityTrackerEngine

router = APIRouter(prefix="/single-molecule-fret-polymerase-fidelity-tracker", tags=["Phase 576 - Autonomous Single-Molecule smFRET High-Fidelity DNA Polymerase Mismatch Proofreading & Exonuclease Kinetic Tracker"])


class SingleMoleculeFretPolymeraseFidelityTrackerAnalyzeRequest(BaseModel):
    name: str = Field(default="Autonomous Single-Molecule smFRET High-Fidelity DNA Polymerase Mismatch Proofreading & Exonuclease Kinetic Tracker Study")
    target_specimen: Optional[str] = Field(default="Dual Cy3/Cy5-Labeled Primer-Template DNA Bound to Thermus aquaticus Polymerase I Active/Exo Sites")
    analytical_modality: Optional[str] = Field(default="smfret-polymerase-fidelity-kinetics")
    input_scale: float = Field(default=1.0, ge=0.1, le=10.0)


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


class SingleMoleculeFretPolymeraseFidelityTrackerStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    fret_efficiency_transition_delta: float
    exonuclease_proofreading_dwell_time_ms: float
    mismatch_discrimination_factor: float
    polymerization_catalytic_rate_nt_s: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []


@router.post("/analyze", response_model=SingleMoleculeFretPolymeraseFidelityTrackerStudyResponse)
async def analyze_single_molecule_fret_polymerase_fidelity_tracker(
    req: SingleMoleculeFretPolymeraseFidelityTrackerAnalyzeRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Execute autonomous analysis for Autonomous Single-Molecule smFRET High-Fidelity DNA Polymerase Mismatch Proofreading & Exonuclease Kinetic Tracker."""
    engine = SingleMoleculeFretPolymeraseFidelityTrackerEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SingleMoleculeFretPolymeraseFidelityTrackerRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        fret_efficiency_transition_delta=result.fret_efficiency_transition_delta,
        exonuclease_proofreading_dwell_time_ms=result.exonuclease_proofreading_dwell_time_ms,
        mismatch_discrimination_factor=result.mismatch_discrimination_factor,
        polymerization_catalytic_rate_nt_s=result.polymerization_catalytic_rate_nt_s,
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

    return SingleMoleculeFretPolymeraseFidelityTrackerStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        fret_efficiency_transition_delta=study.fret_efficiency_transition_delta,
        exonuclease_proofreading_dwell_time_ms=study.exonuclease_proofreading_dwell_time_ms,
        mismatch_discrimination_factor=study.mismatch_discrimination_factor,
        polymerization_catalytic_rate_nt_s=study.polymerization_catalytic_rate_nt_s,
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


@router.get("/studies", response_model=List[SingleMoleculeFretPolymeraseFidelityTrackerStudyResponse])
async def list_single_molecule_fret_polymerase_fidelity_tracker_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Single-Molecule smFRET High-Fidelity DNA Polymerase Mismatch Proofreading & Exonuclease Kinetic Tracker studies."""
    repo = SingleMoleculeFretPolymeraseFidelityTrackerRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SingleMoleculeFretPolymeraseFidelityTrackerStudyResponse)
async def get_single_molecule_fret_polymerase_fidelity_tracker_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Single-Molecule smFRET High-Fidelity DNA Polymerase Mismatch Proofreading & Exonuclease Kinetic Tracker study by ID."""
    repo = SingleMoleculeFretPolymeraseFidelityTrackerRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
