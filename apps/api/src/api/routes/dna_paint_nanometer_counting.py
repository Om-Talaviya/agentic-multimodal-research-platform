"""FastAPI routes for Phase 421: Autonomous DNA-PAINT Nanometer Super-Resolution Spatial Molecular Counting Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.dna_paint_nanometer_counting_repo import DnaPaintNanometerCountingRepository
from research.orchestration.dna_paint_nanometer_counting_engine import DnaPaintNanometerCountingEngine

router = APIRouter(prefix="/dna-paint-nanometer-counting", tags=["dna-paint-nanometer-counting"])


class AnalyzeDnaPaintNanometerCountingRequest(BaseModel):
    name: str = Field(..., example="Autonomous DNA-PAINT Nanometer Super-Resolution Spatial Molecular Counting Engine Run")
    target_specimen: str = Field(default="Nuclear Pore Complex Scaffold with Fluorescent Imager Strands")
    analytical_modality: str = Field(default="dna-paint-counting")
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


class DnaPaintNanometerCountingStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    spatial_localization_precision_nm: float
    absolute_molecule_count: float
    qpaint_binding_frequency_hz: float
    background_dark_time_ratio: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=DnaPaintNanometerCountingStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_dna_paint_nanometer_counting(
    req: AnalyzeDnaPaintNanometerCountingRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous DNA-PAINT Nanometer Super-Resolution Spatial Molecular Counting Engine analysis and persist study."""
    engine = DnaPaintNanometerCountingEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = DnaPaintNanometerCountingRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        spatial_localization_precision_nm=result.spatial_localization_precision_nm,
        absolute_molecule_count=result.absolute_molecule_count,
        qpaint_binding_frequency_hz=result.qpaint_binding_frequency_hz,
        background_dark_time_ratio=result.background_dark_time_ratio,
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

    return DnaPaintNanometerCountingStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        spatial_localization_precision_nm=study.spatial_localization_precision_nm,
        absolute_molecule_count=study.absolute_molecule_count,
        qpaint_binding_frequency_hz=study.qpaint_binding_frequency_hz,
        background_dark_time_ratio=study.background_dark_time_ratio,
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


@router.get("/studies", response_model=List[DnaPaintNanometerCountingStudyResponse])
async def list_dna_paint_nanometer_counting_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous DNA-PAINT Nanometer Super-Resolution Spatial Molecular Counting Engine studies."""
    repo = DnaPaintNanometerCountingRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=DnaPaintNanometerCountingStudyResponse)
async def get_dna_paint_nanometer_counting_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous DNA-PAINT Nanometer Super-Resolution Spatial Molecular Counting Engine study by ID."""
    repo = DnaPaintNanometerCountingRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
