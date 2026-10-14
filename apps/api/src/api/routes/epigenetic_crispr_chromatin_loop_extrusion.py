"""FastAPI routes for Phase 515: Autonomous dCas9-Mediated Chromatin Loop Extrusion & Cohesin-CTCF Boundary Rewriter."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.epigenetic_crispr_chromatin_loop_extrusion_repo import EpigeneticCrisprChromatinLoopExtrusionRepository
from research.orchestration.epigenetic_crispr_chromatin_loop_extrusion_engine import EpigeneticCrisprChromatinLoopExtrusionEngine

router = APIRouter(prefix="/epigenetic-crispr-chromatin-loop-extrusion", tags=["epigenetic-crispr-chromatin-loop-extrusion"])


class AnalyzeEpigeneticCrisprChromatinLoopExtrusionRequest(BaseModel):
    name: str = Field(..., example="Autonomous dCas9-Mediated Chromatin Loop Extrusion & Cohesin-CTCF Boundary Rewriter Run")
    target_specimen: str = Field(default="Human K562 Cells with Chemically Dimerizable dCas9-CTCF Targeted to MYC Super-Enhancer TAD")
    analytical_modality: str = Field(default="crispr-chromatin-loop-rewriting")
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


class EpigeneticCrisprChromatinLoopExtrusionStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    induced_chromatin_loop_contact_frequency_enhancement: float
    insulation_boundary_score_gain: float
    target_oncogene_expression_activation_fold: float
    cohesin_retention_time_at_engineered_ctcf_min: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=EpigeneticCrisprChromatinLoopExtrusionStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_epigenetic_crispr_chromatin_loop_extrusion(
    req: AnalyzeEpigeneticCrisprChromatinLoopExtrusionRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous dCas9-Mediated Chromatin Loop Extrusion & Cohesin-CTCF Boundary Rewriter analysis and persist study."""
    engine = EpigeneticCrisprChromatinLoopExtrusionEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = EpigeneticCrisprChromatinLoopExtrusionRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        induced_chromatin_loop_contact_frequency_enhancement=result.induced_chromatin_loop_contact_frequency_enhancement,
        insulation_boundary_score_gain=result.insulation_boundary_score_gain,
        target_oncogene_expression_activation_fold=result.target_oncogene_expression_activation_fold,
        cohesin_retention_time_at_engineered_ctcf_min=result.cohesin_retention_time_at_engineered_ctcf_min,
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

    return EpigeneticCrisprChromatinLoopExtrusionStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        induced_chromatin_loop_contact_frequency_enhancement=study.induced_chromatin_loop_contact_frequency_enhancement,
        insulation_boundary_score_gain=study.insulation_boundary_score_gain,
        target_oncogene_expression_activation_fold=study.target_oncogene_expression_activation_fold,
        cohesin_retention_time_at_engineered_ctcf_min=study.cohesin_retention_time_at_engineered_ctcf_min,
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


@router.get("/studies", response_model=List[EpigeneticCrisprChromatinLoopExtrusionStudyResponse])
async def list_epigenetic_crispr_chromatin_loop_extrusion_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous dCas9-Mediated Chromatin Loop Extrusion & Cohesin-CTCF Boundary Rewriter studies."""
    repo = EpigeneticCrisprChromatinLoopExtrusionRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=EpigeneticCrisprChromatinLoopExtrusionStudyResponse)
async def get_epigenetic_crispr_chromatin_loop_extrusion_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous dCas9-Mediated Chromatin Loop Extrusion & Cohesin-CTCF Boundary Rewriter study by ID."""
    repo = EpigeneticCrisprChromatinLoopExtrusionRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
