"""FastAPI routes for Phase 463: Autonomous Neural Organoid Spontaneous Synchronous Bursting & Functional Connectivity Grapher."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.neural_organoid_bursting_connectivity_repo import NeuralOrganoidBurstingConnectivityRepository
from research.orchestration.neural_organoid_bursting_connectivity_engine import NeuralOrganoidBurstingConnectivityEngine

router = APIRouter(prefix="/neural-organoid-bursting-connectivity", tags=["neural-organoid-bursting-connectivity"])


class AnalyzeNeuralOrganoidBurstingConnectivityRequest(BaseModel):
    name: str = Field(..., example="Autonomous Neural Organoid Spontaneous Synchronous Bursting & Functional Connectivity Grapher Run")
    target_specimen: str = Field(default="6-Month Human Cerebral Cortical Organoid on 4096-Channel CMOS High-Density MEA")
    analytical_modality: str = Field(default="organoid-neural-connectivity")
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


class NeuralOrganoidBurstingConnectivityStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    synchronous_network_burst_rate_hz: float
    graph_small_world_clustering_coefficient: float
    cross_correlation_functional_connectivity_density: float
    shannon_entropy_burst_complexity: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=NeuralOrganoidBurstingConnectivityStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_neural_organoid_bursting_connectivity(
    req: AnalyzeNeuralOrganoidBurstingConnectivityRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Neural Organoid Spontaneous Synchronous Bursting & Functional Connectivity Grapher analysis and persist study."""
    engine = NeuralOrganoidBurstingConnectivityEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = NeuralOrganoidBurstingConnectivityRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        synchronous_network_burst_rate_hz=result.synchronous_network_burst_rate_hz,
        graph_small_world_clustering_coefficient=result.graph_small_world_clustering_coefficient,
        cross_correlation_functional_connectivity_density=result.cross_correlation_functional_connectivity_density,
        shannon_entropy_burst_complexity=result.shannon_entropy_burst_complexity,
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

    return NeuralOrganoidBurstingConnectivityStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        synchronous_network_burst_rate_hz=study.synchronous_network_burst_rate_hz,
        graph_small_world_clustering_coefficient=study.graph_small_world_clustering_coefficient,
        cross_correlation_functional_connectivity_density=study.cross_correlation_functional_connectivity_density,
        shannon_entropy_burst_complexity=study.shannon_entropy_burst_complexity,
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


@router.get("/studies", response_model=List[NeuralOrganoidBurstingConnectivityStudyResponse])
async def list_neural_organoid_bursting_connectivity_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Neural Organoid Spontaneous Synchronous Bursting & Functional Connectivity Grapher studies."""
    repo = NeuralOrganoidBurstingConnectivityRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=NeuralOrganoidBurstingConnectivityStudyResponse)
async def get_neural_organoid_bursting_connectivity_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Neural Organoid Spontaneous Synchronous Bursting & Functional Connectivity Grapher study by ID."""
    repo = NeuralOrganoidBurstingConnectivityRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
