"""FastAPI route for Phase 577: Autonomous Microfluidic Droplet-Based Directed Evolution & Enzyme Fitness Landscape Navigator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.microfluidic_droplet_directed_evolution_repo import MicrofluidicDropletDirectedEvolutionRepository
from research.orchestration.microfluidic_droplet_directed_evolution_engine import MicrofluidicDropletDirectedEvolutionEngine

router = APIRouter(prefix="/microfluidic-droplet-directed-evolution", tags=["Phase 577 - Autonomous Microfluidic Droplet-Based Directed Evolution & Enzyme Fitness Landscape Navigator"])


class MicrofluidicDropletDirectedEvolutionAnalyzeRequest(BaseModel):
    name: str = Field(default="Autonomous Microfluidic Droplet-Based Directed Evolution & Enzyme Fitness Landscape Navigator Study")
    target_specimen: Optional[str] = Field(default="Picoliter Water-in-Oil Droplet Encapsulated TEM-1 β-Lactamase Saturation Mutagenesis Library")
    analytical_modality: Optional[str] = Field(default="microfluidic-droplet-directed-evolution")
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


class MicrofluidicDropletDirectedEvolutionStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    droplet_generation_rate_hz: float
    enzyme_kcat_fold_improvement: float
    fitness_landscape_ruggedness_index: float
    epistatic_interaction_coefficient: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []


@router.post("/analyze", response_model=MicrofluidicDropletDirectedEvolutionStudyResponse)
async def analyze_microfluidic_droplet_directed_evolution(
    req: MicrofluidicDropletDirectedEvolutionAnalyzeRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Execute autonomous analysis for Autonomous Microfluidic Droplet-Based Directed Evolution & Enzyme Fitness Landscape Navigator."""
    engine = MicrofluidicDropletDirectedEvolutionEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = MicrofluidicDropletDirectedEvolutionRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        droplet_generation_rate_hz=result.droplet_generation_rate_hz,
        enzyme_kcat_fold_improvement=result.enzyme_kcat_fold_improvement,
        fitness_landscape_ruggedness_index=result.fitness_landscape_ruggedness_index,
        epistatic_interaction_coefficient=result.epistatic_interaction_coefficient,
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

    return MicrofluidicDropletDirectedEvolutionStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        droplet_generation_rate_hz=study.droplet_generation_rate_hz,
        enzyme_kcat_fold_improvement=study.enzyme_kcat_fold_improvement,
        fitness_landscape_ruggedness_index=study.fitness_landscape_ruggedness_index,
        epistatic_interaction_coefficient=study.epistatic_interaction_coefficient,
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


@router.get("/studies", response_model=List[MicrofluidicDropletDirectedEvolutionStudyResponse])
async def list_microfluidic_droplet_directed_evolution_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Microfluidic Droplet-Based Directed Evolution & Enzyme Fitness Landscape Navigator studies."""
    repo = MicrofluidicDropletDirectedEvolutionRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=MicrofluidicDropletDirectedEvolutionStudyResponse)
async def get_microfluidic_droplet_directed_evolution_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Microfluidic Droplet-Based Directed Evolution & Enzyme Fitness Landscape Navigator study by ID."""
    repo = MicrofluidicDropletDirectedEvolutionRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
