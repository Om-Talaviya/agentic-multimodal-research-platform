"""FastAPI routes for Phase 492: Autonomous Multi-Organ Microphysiological Human-on-a-Chip Endocrine-Metabolic Feedback Loop."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.human_on_chip_endocrine_feedback_repo import HumanOnChipEndocrineFeedbackRepository
from research.orchestration.human_on_chip_endocrine_feedback_engine import HumanOnChipEndocrineFeedbackEngine

router = APIRouter(prefix="/human-on-chip-endocrine-feedback", tags=["human-on-chip-endocrine-feedback"])


class AnalyzeHumanOnChipEndocrineFeedbackRequest(BaseModel):
    name: str = Field(..., example="Autonomous Multi-Organ Microphysiological Human-on-a-Chip Endocrine-Metabolic Feedback Loop Run")
    target_specimen: str = Field(default="4-Organ Interconnected Microfluidic Platform (Liver Spheroids, Islet Organoids, Adipose, Skeletal Muscle)")
    analytical_modality: str = Field(default="human-on-chip-endocrine-loop")
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


class HumanOnChipEndocrineFeedbackStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    glucose_stimulated_insulin_secretion_gsis_index: float
    hepatic_glucose_uptake_rate_uM_per_hr: float
    inter_organ_circulatory_perfusion_flow_uL_per_min: float
    homeostatic_endocrine_feedback_sync_tau: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=HumanOnChipEndocrineFeedbackStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_human_on_chip_endocrine_feedback(
    req: AnalyzeHumanOnChipEndocrineFeedbackRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Multi-Organ Microphysiological Human-on-a-Chip Endocrine-Metabolic Feedback Loop analysis and persist study."""
    engine = HumanOnChipEndocrineFeedbackEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = HumanOnChipEndocrineFeedbackRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        glucose_stimulated_insulin_secretion_gsis_index=result.glucose_stimulated_insulin_secretion_gsis_index,
        hepatic_glucose_uptake_rate_uM_per_hr=result.hepatic_glucose_uptake_rate_uM_per_hr,
        inter_organ_circulatory_perfusion_flow_uL_per_min=result.inter_organ_circulatory_perfusion_flow_uL_per_min,
        homeostatic_endocrine_feedback_sync_tau=result.homeostatic_endocrine_feedback_sync_tau,
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

    return HumanOnChipEndocrineFeedbackStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        glucose_stimulated_insulin_secretion_gsis_index=study.glucose_stimulated_insulin_secretion_gsis_index,
        hepatic_glucose_uptake_rate_uM_per_hr=study.hepatic_glucose_uptake_rate_uM_per_hr,
        inter_organ_circulatory_perfusion_flow_uL_per_min=study.inter_organ_circulatory_perfusion_flow_uL_per_min,
        homeostatic_endocrine_feedback_sync_tau=study.homeostatic_endocrine_feedback_sync_tau,
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


@router.get("/studies", response_model=List[HumanOnChipEndocrineFeedbackStudyResponse])
async def list_human_on_chip_endocrine_feedback_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Multi-Organ Microphysiological Human-on-a-Chip Endocrine-Metabolic Feedback Loop studies."""
    repo = HumanOnChipEndocrineFeedbackRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=HumanOnChipEndocrineFeedbackStudyResponse)
async def get_human_on_chip_endocrine_feedback_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Multi-Organ Microphysiological Human-on-a-Chip Endocrine-Metabolic Feedback Loop study by ID."""
    repo = HumanOnChipEndocrineFeedbackRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
