"""FastAPI routes for Phase 504: Autonomous High-Throughput Droplet Microfluidic Ultra-Fast Directed Enzyme Evolution Kinetic Screener."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.droplet_microfluidic_enzyme_evolution_repo import DropletMicrofluidicEnzymeEvolutionRepository
from research.orchestration.droplet_microfluidic_enzyme_evolution_engine import DropletMicrofluidicEnzymeEvolutionEngine

router = APIRouter(prefix="/droplet-microfluidic-enzyme-evolution", tags=["droplet-microfluidic-enzyme-evolution"])


class AnalyzeDropletMicrofluidicEnzymeEvolutionRequest(BaseModel):
    name: str = Field(..., example="Autonomous High-Throughput Droplet Microfluidic Ultra-Fast Directed Enzyme Evolution Kinetic Screener Run")
    target_specimen: str = Field(default="Picoliter Droplet Emulsion Library of Variant PETase Esterases with Fluorescent Fluorogenic Substrates")
    analytical_modality: str = Field(default="droplet-microfluidic-enzyme-screening")
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


class DropletMicrofluidicEnzymeEvolutionStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    catalytic_efficiency_improvement_fold: float
    screening_throughput_droplets_per_second: float
    false_discovery_rate_q_value: float
    thermostability_delta_tm_celsius: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=DropletMicrofluidicEnzymeEvolutionStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_droplet_microfluidic_enzyme_evolution(
    req: AnalyzeDropletMicrofluidicEnzymeEvolutionRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous High-Throughput Droplet Microfluidic Ultra-Fast Directed Enzyme Evolution Kinetic Screener analysis and persist study."""
    engine = DropletMicrofluidicEnzymeEvolutionEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = DropletMicrofluidicEnzymeEvolutionRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        catalytic_efficiency_improvement_fold=result.catalytic_efficiency_improvement_fold,
        screening_throughput_droplets_per_second=result.screening_throughput_droplets_per_second,
        false_discovery_rate_q_value=result.false_discovery_rate_q_value,
        thermostability_delta_tm_celsius=result.thermostability_delta_tm_celsius,
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

    return DropletMicrofluidicEnzymeEvolutionStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        catalytic_efficiency_improvement_fold=study.catalytic_efficiency_improvement_fold,
        screening_throughput_droplets_per_second=study.screening_throughput_droplets_per_second,
        false_discovery_rate_q_value=study.false_discovery_rate_q_value,
        thermostability_delta_tm_celsius=study.thermostability_delta_tm_celsius,
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


@router.get("/studies", response_model=List[DropletMicrofluidicEnzymeEvolutionStudyResponse])
async def list_droplet_microfluidic_enzyme_evolution_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous High-Throughput Droplet Microfluidic Ultra-Fast Directed Enzyme Evolution Kinetic Screener studies."""
    repo = DropletMicrofluidicEnzymeEvolutionRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=DropletMicrofluidicEnzymeEvolutionStudyResponse)
async def get_droplet_microfluidic_enzyme_evolution_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous High-Throughput Droplet Microfluidic Ultra-Fast Directed Enzyme Evolution Kinetic Screener study by ID."""
    repo = DropletMicrofluidicEnzymeEvolutionRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
