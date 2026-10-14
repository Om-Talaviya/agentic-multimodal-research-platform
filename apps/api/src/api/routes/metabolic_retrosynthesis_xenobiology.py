"""FastAPI routes for Phase 507: Autonomous Non-Natural Xenobiotic Pathway Metabolic Retrosynthesis Generator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.metabolic_retrosynthesis_xenobiology_repo import MetabolicRetrosynthesisXenobiologyRepository
from research.orchestration.metabolic_retrosynthesis_xenobiology_engine import MetabolicRetrosynthesisXenobiologyEngine

router = APIRouter(prefix="/metabolic-retrosynthesis-xenobiology", tags=["metabolic-retrosynthesis-xenobiology"])


class AnalyzeMetabolicRetrosynthesisXenobiologyRequest(BaseModel):
    name: str = Field(..., example="Autonomous Non-Natural Xenobiotic Pathway Metabolic Retrosynthesis Generator Run")
    target_specimen: str = Field(default="In-Silico Retrosynthetic Reaction Network for 1,3-Diaminopropane Biosynthesis via Novel Enzymes")
    analytical_modality: str = Field(default="xenobiotic-retrosynthesis-flux")
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


class MetabolicRetrosynthesisXenobiologyStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    retrosynthetic_pathway_plausibility_score: float
    thermodynamic_driving_force_delta_G_kj_mol: float
    theoretical_maximum_carbon_yield_pct: float
    chassis_endogenous_flux_perturbation_index: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=MetabolicRetrosynthesisXenobiologyStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_metabolic_retrosynthesis_xenobiology(
    req: AnalyzeMetabolicRetrosynthesisXenobiologyRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Non-Natural Xenobiotic Pathway Metabolic Retrosynthesis Generator analysis and persist study."""
    engine = MetabolicRetrosynthesisXenobiologyEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = MetabolicRetrosynthesisXenobiologyRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        retrosynthetic_pathway_plausibility_score=result.retrosynthetic_pathway_plausibility_score,
        thermodynamic_driving_force_delta_G_kj_mol=result.thermodynamic_driving_force_delta_G_kj_mol,
        theoretical_maximum_carbon_yield_pct=result.theoretical_maximum_carbon_yield_pct,
        chassis_endogenous_flux_perturbation_index=result.chassis_endogenous_flux_perturbation_index,
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

    return MetabolicRetrosynthesisXenobiologyStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        retrosynthetic_pathway_plausibility_score=study.retrosynthetic_pathway_plausibility_score,
        thermodynamic_driving_force_delta_G_kj_mol=study.thermodynamic_driving_force_delta_G_kj_mol,
        theoretical_maximum_carbon_yield_pct=study.theoretical_maximum_carbon_yield_pct,
        chassis_endogenous_flux_perturbation_index=study.chassis_endogenous_flux_perturbation_index,
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


@router.get("/studies", response_model=List[MetabolicRetrosynthesisXenobiologyStudyResponse])
async def list_metabolic_retrosynthesis_xenobiology_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Non-Natural Xenobiotic Pathway Metabolic Retrosynthesis Generator studies."""
    repo = MetabolicRetrosynthesisXenobiologyRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=MetabolicRetrosynthesisXenobiologyStudyResponse)
async def get_metabolic_retrosynthesis_xenobiology_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Non-Natural Xenobiotic Pathway Metabolic Retrosynthesis Generator study by ID."""
    repo = MetabolicRetrosynthesisXenobiologyRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
