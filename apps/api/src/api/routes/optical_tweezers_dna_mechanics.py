"""FastAPI routes for Phase 416: Autonomous Optical Tweezers DNA-Protein Mechanical Tension & Force-Extension Overstretching Modeler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.optical_tweezers_dna_mechanics_repo import OpticalTweezersDnaMechanicsRepository
from research.orchestration.optical_tweezers_dna_mechanics_engine import OpticalTweezersDnaMechanicsEngine

router = APIRouter(prefix="/optical-tweezers-dna-mechanics", tags=["optical-tweezers-dna-mechanics"])


class AnalyzeOpticalTweezersDnaMechanicsRequest(BaseModel):
    name: str = Field(..., example="Autonomous Optical Tweezers DNA-Protein Mechanical Tension & Force-Extension Overstretching Modeler Run")
    target_specimen: str = Field(default="Single-Molecule Lambda-DNA Tether with RecA Nucleoprotein")
    analytical_modality: str = Field(default="optical-tweezers")
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


class OpticalTweezersDnaMechanicsStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    overstretching_transition_force_pN: float
    persistence_length_nm: float
    contour_length_um: float
    trap_stiffness_pN_per_nm: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=OpticalTweezersDnaMechanicsStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_optical_tweezers_dna_mechanics(
    req: AnalyzeOpticalTweezersDnaMechanicsRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Optical Tweezers DNA-Protein Mechanical Tension & Force-Extension Overstretching Modeler analysis and persist study."""
    engine = OpticalTweezersDnaMechanicsEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = OpticalTweezersDnaMechanicsRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        overstretching_transition_force_pN=result.overstretching_transition_force_pN,
        persistence_length_nm=result.persistence_length_nm,
        contour_length_um=result.contour_length_um,
        trap_stiffness_pN_per_nm=result.trap_stiffness_pN_per_nm,
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

    return OpticalTweezersDnaMechanicsStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        overstretching_transition_force_pN=study.overstretching_transition_force_pN,
        persistence_length_nm=study.persistence_length_nm,
        contour_length_um=study.contour_length_um,
        trap_stiffness_pN_per_nm=study.trap_stiffness_pN_per_nm,
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


@router.get("/studies", response_model=List[OpticalTweezersDnaMechanicsStudyResponse])
async def list_optical_tweezers_dna_mechanics_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Optical Tweezers DNA-Protein Mechanical Tension & Force-Extension Overstretching Modeler studies."""
    repo = OpticalTweezersDnaMechanicsRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=OpticalTweezersDnaMechanicsStudyResponse)
async def get_optical_tweezers_dna_mechanics_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Optical Tweezers DNA-Protein Mechanical Tension & Force-Extension Overstretching Modeler study by ID."""
    repo = OpticalTweezersDnaMechanicsRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
