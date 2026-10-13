"""FastAPI routes for Phase 450: Autonomous Nanopore Ionic Current Blockade Shape Classifier for Macromolecular Topologies."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.nanopore_blockade_topology_classifier_repo import NanoporeBlockadeTopologyRepository
from research.orchestration.nanopore_blockade_topology_classifier_engine import NanoporeBlockadeTopologyEngine

router = APIRouter(prefix="/nanopore-blockade-topology", tags=["nanopore-blockade-topology"])


class AnalyzeNanoporeBlockadeTopologyRequest(BaseModel):
    name: str = Field(..., example="Autonomous Nanopore Ionic Current Blockade Shape Classifier for Macromolecular Topologies Run")
    target_specimen: str = Field(default="Supercoiled Plasmid DNA and Knotted Circular Peptides Passing Through 4nm Aerolysin Pore")
    analytical_modality: str = Field(default="nanopore-blockade-topology")
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


class NanoporeBlockadeTopologyStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    dwell_time_topological_knot_us: float
    fractional_blockade_current_depth_ratio: float
    topology_classification_accuracy: float
    translocation_velocity_nt_per_ms: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=NanoporeBlockadeTopologyStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_nanopore_blockade_topology_classifier(
    req: AnalyzeNanoporeBlockadeTopologyRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Nanopore Ionic Current Blockade Shape Classifier for Macromolecular Topologies analysis and persist study."""
    engine = NanoporeBlockadeTopologyEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = NanoporeBlockadeTopologyRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        dwell_time_topological_knot_us=result.dwell_time_topological_knot_us,
        fractional_blockade_current_depth_ratio=result.fractional_blockade_current_depth_ratio,
        topology_classification_accuracy=result.topology_classification_accuracy,
        translocation_velocity_nt_per_ms=result.translocation_velocity_nt_per_ms,
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

    return NanoporeBlockadeTopologyStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        dwell_time_topological_knot_us=study.dwell_time_topological_knot_us,
        fractional_blockade_current_depth_ratio=study.fractional_blockade_current_depth_ratio,
        topology_classification_accuracy=study.topology_classification_accuracy,
        translocation_velocity_nt_per_ms=study.translocation_velocity_nt_per_ms,
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


@router.get("/studies", response_model=List[NanoporeBlockadeTopologyStudyResponse])
async def list_nanopore_blockade_topology_classifier_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Nanopore Ionic Current Blockade Shape Classifier for Macromolecular Topologies studies."""
    repo = NanoporeBlockadeTopologyRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=NanoporeBlockadeTopologyStudyResponse)
async def get_nanopore_blockade_topology_classifier_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Nanopore Ionic Current Blockade Shape Classifier for Macromolecular Topologies study by ID."""
    repo = NanoporeBlockadeTopologyRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
