"""FastAPI routes for Phase 414: Autonomous Cryo-FIB Milling & In-Situ Lamella Thickness Optimization Engine Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.cryo_fib_milling_repo import CryoFibMillingRepository
from research.orchestration.cryo_fib_milling_engine import CryoFibMillingEngine

router = APIRouter(prefix="/cryo-fib-milling", tags=["cryo-fib-milling"])


class AnalyzeCryoFibMillingRequest(BaseModel):
    name: str = Field(..., example="Autonomous Cryo-FIB Milling In-Situ Lamella Thinning Run")
    target_specimen: str = Field(default="Vitreous Cellular Cryo-Lamella")
    analytical_modality: str = Field(default="cryo-fib-milling")
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


class CryoFibMillingStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    in_situ_lamella_thickness_nm: float
    curtaining_artifact_suppression_ratio: float
    gallium_ion_beam_current_pA: float
    vitreous_ice_preservation_score: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=CryoFibMillingStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_cryo_fib_milling(
    req: AnalyzeCryoFibMillingRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Cryo-FIB Milling & In-Situ Lamella Thickness Optimization analysis and persist study record."""
    engine = CryoFibMillingEngine()
    analysis = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = CryoFibMillingRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=analysis.target_specimen,
        analytical_modality=analysis.analytical_modality,
        in_situ_lamella_thickness_nm=analysis.in_situ_lamella_thickness_nm,
        curtaining_artifact_suppression_ratio=analysis.curtaining_artifact_suppression_ratio,
        gallium_ion_beam_current_pA=analysis.gallium_ion_beam_current_pA,
        vitreous_ice_preservation_score=analysis.vitreous_ice_preservation_score,
        confidence_score=analysis.confidence_score,
        status="completed",
        summary_report=analysis.summary_report,
    )

    for item in analysis.item_profiles:
        await repo.add_item_profile(
            study_id=study.id,
            item_name=item.item_name,
            profile_category=item.profile_category,
            quantitative_value=item.quantitative_value,
            log2_fold_change=item.log2_fold_change,
            significance_score=item.significance_score,
        )

    for trace in analysis.metric_traces:
        await repo.add_metric_trace(
            study_id=study.id,
            metric_dimension=trace.metric_dimension,
            observed_value=trace.observed_value,
            z_score=trace.z_score,
            p_value=trace.p_value,
        )

    return CryoFibMillingStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        in_situ_lamella_thickness_nm=study.in_situ_lamella_thickness_nm,
        curtaining_artifact_suppression_ratio=study.curtaining_artifact_suppression_ratio,
        gallium_ion_beam_current_pA=study.gallium_ion_beam_current_pA,
        vitreous_ice_preservation_score=study.vitreous_ice_preservation_score,
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
            ) for it in analysis.item_profiles
        ],
        metric_traces=[
            MetricTraceResponse(
                metric_dimension=tr.metric_dimension,
                observed_value=tr.observed_value,
                z_score=tr.z_score,
                p_value=tr.p_value,
            ) for tr in analysis.metric_traces
        ],
    )


@router.get("/studies", response_model=List[CryoFibMillingStudyResponse])
async def list_cryo_fib_milling_studies(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
):
    """List all Cryo-FIB Milling studies."""
    repo = CryoFibMillingRepository(session)
    return await repo.list_studies(limit=limit, offset=offset)


@router.get("/studies/{study_id}", response_model=CryoFibMillingStudyResponse)
async def get_cryo_fib_milling_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve a specific Cryo-FIB Milling study by ID."""
    repo = CryoFibMillingRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryo-FIB Milling study with ID {study_id} not found.",
        )
    return study
