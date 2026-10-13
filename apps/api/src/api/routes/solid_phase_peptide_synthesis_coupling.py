"""FastAPI routes for Phase 445: Autonomous High-Density Solid-Phase Peptide Synthesis (SPPS) Coupling Yield & Aggregation Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.solid_phase_peptide_synthesis_coupling_repo import SolidPhasePeptideSynthesisRepository
from research.orchestration.solid_phase_peptide_synthesis_coupling_engine import SolidPhasePeptideSynthesisEngine

router = APIRouter(prefix="/solid-phase-peptide-synthesis", tags=["solid-phase-peptide-synthesis"])


class AnalyzeSolidPhasePeptideSynthesisRequest(BaseModel):
    name: str = Field(..., example="Autonomous High-Density Solid-Phase Peptide Synthesis (SPPS) Coupling Yield & Aggregation Engine Run")
    target_specimen: str = Field(default="40-Mer Hydrophobic Amyloid-Beta Peptide Intermediate on Wang Resin Microbeads")
    analytical_modality: str = Field(default="solid-phase-peptide-synthesis")
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


class SolidPhasePeptideSynthesisStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    fmoc_deprotection_efficiency_ratio: float
    coupling_reaction_half_life_seconds: float
    aggregation_beta_sheet_propensity: float
    purity_crude_hplc_percentage: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=SolidPhasePeptideSynthesisStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_solid_phase_peptide_synthesis_coupling(
    req: AnalyzeSolidPhasePeptideSynthesisRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous High-Density Solid-Phase Peptide Synthesis (SPPS) Coupling Yield & Aggregation Engine analysis and persist study."""
    engine = SolidPhasePeptideSynthesisEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SolidPhasePeptideSynthesisRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        fmoc_deprotection_efficiency_ratio=result.fmoc_deprotection_efficiency_ratio,
        coupling_reaction_half_life_seconds=result.coupling_reaction_half_life_seconds,
        aggregation_beta_sheet_propensity=result.aggregation_beta_sheet_propensity,
        purity_crude_hplc_percentage=result.purity_crude_hplc_percentage,
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

    return SolidPhasePeptideSynthesisStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        fmoc_deprotection_efficiency_ratio=study.fmoc_deprotection_efficiency_ratio,
        coupling_reaction_half_life_seconds=study.coupling_reaction_half_life_seconds,
        aggregation_beta_sheet_propensity=study.aggregation_beta_sheet_propensity,
        purity_crude_hplc_percentage=study.purity_crude_hplc_percentage,
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


@router.get("/studies", response_model=List[SolidPhasePeptideSynthesisStudyResponse])
async def list_solid_phase_peptide_synthesis_coupling_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous High-Density Solid-Phase Peptide Synthesis (SPPS) Coupling Yield & Aggregation Engine studies."""
    repo = SolidPhasePeptideSynthesisRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SolidPhasePeptideSynthesisStudyResponse)
async def get_solid_phase_peptide_synthesis_coupling_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous High-Density Solid-Phase Peptide Synthesis (SPPS) Coupling Yield & Aggregation Engine study by ID."""
    repo = SolidPhasePeptideSynthesisRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
