"""FastAPI routes for Phase 427: Autonomous CRISPR C-to-G Base Editor (CGBE) & Cas12f Miniature Transposon Editing Forecaster."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.cgbe_cas12f_miniature_editing_repo import CgbeCas12fMiniatureEditingRepository
from research.orchestration.cgbe_cas12f_miniature_editing_engine import CgbeCas12fMiniatureEditingEngine

router = APIRouter(prefix="/cgbe-cas12f-miniature-editing", tags=["cgbe-cas12f-miniature-editing"])


class AnalyzeCgbeCas12fMiniatureEditingRequest(BaseModel):
    name: str = Field(..., example="Autonomous CRISPR C-to-G Base Editor (CGBE) & Cas12f Miniature Transposon Editing Forecaster Run")
    target_specimen: str = Field(default="Ultra-Compact Cas12f Miniature CGBE Complex in AAV Vector")
    analytical_modality: str = Field(default="cgbe-cas12f-editing")
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


class CgbeCas12fMiniatureEditingStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    c_to_g_conversion_purity_percent: float
    on_target_indel_frequency_percent: float
    aav_packaging_size_kb: float
    off_target_cleavage_fraction: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=CgbeCas12fMiniatureEditingStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_cgbe_cas12f_miniature_editing(
    req: AnalyzeCgbeCas12fMiniatureEditingRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous CRISPR C-to-G Base Editor (CGBE) & Cas12f Miniature Transposon Editing Forecaster analysis and persist study."""
    engine = CgbeCas12fMiniatureEditingEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = CgbeCas12fMiniatureEditingRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        c_to_g_conversion_purity_percent=result.c_to_g_conversion_purity_percent,
        on_target_indel_frequency_percent=result.on_target_indel_frequency_percent,
        aav_packaging_size_kb=result.aav_packaging_size_kb,
        off_target_cleavage_fraction=result.off_target_cleavage_fraction,
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

    return CgbeCas12fMiniatureEditingStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        c_to_g_conversion_purity_percent=study.c_to_g_conversion_purity_percent,
        on_target_indel_frequency_percent=study.on_target_indel_frequency_percent,
        aav_packaging_size_kb=study.aav_packaging_size_kb,
        off_target_cleavage_fraction=study.off_target_cleavage_fraction,
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


@router.get("/studies", response_model=List[CgbeCas12fMiniatureEditingStudyResponse])
async def list_cgbe_cas12f_miniature_editing_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous CRISPR C-to-G Base Editor (CGBE) & Cas12f Miniature Transposon Editing Forecaster studies."""
    repo = CgbeCas12fMiniatureEditingRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=CgbeCas12fMiniatureEditingStudyResponse)
async def get_cgbe_cas12f_miniature_editing_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous CRISPR C-to-G Base Editor (CGBE) & Cas12f Miniature Transposon Editing Forecaster study by ID."""
    repo = CgbeCas12fMiniatureEditingRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
