"""FastAPI routes for Phase 566: Autonomous Programmable RNA-Targeted ADAR Deaminase Epitranscriptomic Editing Window Predictor."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.rna_targeted_adar_deaminase_editing_repo import RnaTargetedAdarDeaminaseEditingRepository
from research.orchestration.rna_targeted_adar_deaminase_editing_engine import RnaTargetedAdarDeaminaseEditingEngine

router = APIRouter(prefix="/rna-targeted-adar-deaminase-editing", tags=["rna-targeted-adar-deaminase-editing"])


class AnalyzeRnaTargetedAdarDeaminaseEditingRequest(BaseModel):
    name: str = Field(..., example="Autonomous Programmable RNA-Targeted ADAR Deaminase Epitranscriptomic Editing Window Predictor Run")
    target_specimen: str = Field(default="Endogenous Human ADAR2 Deaminase recruited via Circular Guide RNA (arRNA) targeting Premature Stop Codons in MECP2 mRNA")
    analytical_modality: str = Field(default="programmable-adar-rna-editing")
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


class RnaTargetedAdarDeaminaseEditingStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    targeted_adenosine_to_inosine_editing_efficiency_pct: float
    bystander_adenosine_deamination_rate_pct: float
    guide_circular_rna_stability_half_life_hours: float
    target_transcript_restoration_fold: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=RnaTargetedAdarDeaminaseEditingStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_rna_targeted_adar_deaminase_editing(
    req: AnalyzeRnaTargetedAdarDeaminaseEditingRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Programmable RNA-Targeted ADAR Deaminase Epitranscriptomic Editing Window Predictor analysis and persist study."""
    engine = RnaTargetedAdarDeaminaseEditingEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = RnaTargetedAdarDeaminaseEditingRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        targeted_adenosine_to_inosine_editing_efficiency_pct=result.targeted_adenosine_to_inosine_editing_efficiency_pct,
        bystander_adenosine_deamination_rate_pct=result.bystander_adenosine_deamination_rate_pct,
        guide_circular_rna_stability_half_life_hours=result.guide_circular_rna_stability_half_life_hours,
        target_transcript_restoration_fold=result.target_transcript_restoration_fold,
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

    return RnaTargetedAdarDeaminaseEditingStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        targeted_adenosine_to_inosine_editing_efficiency_pct=study.targeted_adenosine_to_inosine_editing_efficiency_pct,
        bystander_adenosine_deamination_rate_pct=study.bystander_adenosine_deamination_rate_pct,
        guide_circular_rna_stability_half_life_hours=study.guide_circular_rna_stability_half_life_hours,
        target_transcript_restoration_fold=study.target_transcript_restoration_fold,
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


@router.get("/studies", response_model=List[RnaTargetedAdarDeaminaseEditingStudyResponse])
async def list_rna_targeted_adar_deaminase_editing_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Programmable RNA-Targeted ADAR Deaminase Epitranscriptomic Editing Window Predictor studies."""
    repo = RnaTargetedAdarDeaminaseEditingRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=RnaTargetedAdarDeaminaseEditingStudyResponse)
async def get_rna_targeted_adar_deaminase_editing_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Programmable RNA-Targeted ADAR Deaminase Epitranscriptomic Editing Window Predictor study by ID."""
    repo = RnaTargetedAdarDeaminaseEditingRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
