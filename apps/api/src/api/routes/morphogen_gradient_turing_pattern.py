"""FastAPI routes for Phase 456: Autonomous Morphogen Gradient Diffusion-Turing Pattern Self-Organization Simulator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.morphogen_gradient_turing_pattern_repo import MorphogenGradientTuringPatternRepository
from research.orchestration.morphogen_gradient_turing_pattern_engine import MorphogenGradientTuringPatternEngine

router = APIRouter(prefix="/morphogen-gradient-turing-pattern", tags=["morphogen-gradient-turing-pattern"])


class AnalyzeMorphogenGradientTuringPatternRequest(BaseModel):
    name: str = Field(..., example="Autonomous Morphogen Gradient Diffusion-Turing Pattern Self-Organization Simulator Run")
    target_specimen: str = Field(default="Synthetic Multicellular Embryoid with Nodal/Lefty Reaction-Diffusion Pattern Formation")
    analytical_modality: str = Field(default="morphogen-turing-morphogenesis")
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


class MorphogenGradientTuringPatternStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    turing_instability_wavelength_um: float
    nodal_diffusion_coefficient_um2_per_s: float
    pattern_symmetry_breaking_order_parameter: float
    tissue_axis_polarization_ratio: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=MorphogenGradientTuringPatternStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_morphogen_gradient_turing_pattern(
    req: AnalyzeMorphogenGradientTuringPatternRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Morphogen Gradient Diffusion-Turing Pattern Self-Organization Simulator analysis and persist study."""
    engine = MorphogenGradientTuringPatternEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = MorphogenGradientTuringPatternRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        turing_instability_wavelength_um=result.turing_instability_wavelength_um,
        nodal_diffusion_coefficient_um2_per_s=result.nodal_diffusion_coefficient_um2_per_s,
        pattern_symmetry_breaking_order_parameter=result.pattern_symmetry_breaking_order_parameter,
        tissue_axis_polarization_ratio=result.tissue_axis_polarization_ratio,
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

    return MorphogenGradientTuringPatternStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        turing_instability_wavelength_um=study.turing_instability_wavelength_um,
        nodal_diffusion_coefficient_um2_per_s=study.nodal_diffusion_coefficient_um2_per_s,
        pattern_symmetry_breaking_order_parameter=study.pattern_symmetry_breaking_order_parameter,
        tissue_axis_polarization_ratio=study.tissue_axis_polarization_ratio,
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


@router.get("/studies", response_model=List[MorphogenGradientTuringPatternStudyResponse])
async def list_morphogen_gradient_turing_pattern_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Morphogen Gradient Diffusion-Turing Pattern Self-Organization Simulator studies."""
    repo = MorphogenGradientTuringPatternRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=MorphogenGradientTuringPatternStudyResponse)
async def get_morphogen_gradient_turing_pattern_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Morphogen Gradient Diffusion-Turing Pattern Self-Organization Simulator study by ID."""
    repo = MorphogenGradientTuringPatternRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
