"""FastAPI routes for Phase 451: Autonomous Single-Molecule Optical Tweezers Ribosome Translation Kinetic Polypeptide Translocation Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.optical_tweezers_ribosome_translation_repo import OpticalTweezersRibosomeTranslationRepository
from research.orchestration.optical_tweezers_ribosome_translation_engine import OpticalTweezersRibosomeTranslationEngine

router = APIRouter(prefix="/optical-tweezers-ribosome-translation", tags=["optical-tweezers-ribosome-translation"])


class AnalyzeOpticalTweezersRibosomeTranslationRequest(BaseModel):
    name: str = Field(..., example="Autonomous Single-Molecule Optical Tweezers Ribosome Translation Kinetic Polypeptide Translocation Engine Run")
    target_specimen: str = Field(default="70S Bacterial Ribosome Translating Structured mRNA Stem-Loop under Constant Force (12 pN)")
    analytical_modality: str = Field(default="ribosome-translation-dynamics")
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


class OpticalTweezersRibosomeTranslationStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    codon_stepping_dwell_time_ms: float
    mrna_unfolding_barrier_activation_energy_kb_t: float
    frameshift_slippage_probability: float
    elongation_rate_amino_acids_per_s: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=OpticalTweezersRibosomeTranslationStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_optical_tweezers_ribosome_translation(
    req: AnalyzeOpticalTweezersRibosomeTranslationRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Single-Molecule Optical Tweezers Ribosome Translation Kinetic Polypeptide Translocation Engine analysis and persist study."""
    engine = OpticalTweezersRibosomeTranslationEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = OpticalTweezersRibosomeTranslationRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        codon_stepping_dwell_time_ms=result.codon_stepping_dwell_time_ms,
        mrna_unfolding_barrier_activation_energy_kb_t=result.mrna_unfolding_barrier_activation_energy_kb_t,
        frameshift_slippage_probability=result.frameshift_slippage_probability,
        elongation_rate_amino_acids_per_s=result.elongation_rate_amino_acids_per_s,
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

    return OpticalTweezersRibosomeTranslationStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        codon_stepping_dwell_time_ms=study.codon_stepping_dwell_time_ms,
        mrna_unfolding_barrier_activation_energy_kb_t=study.mrna_unfolding_barrier_activation_energy_kb_t,
        frameshift_slippage_probability=study.frameshift_slippage_probability,
        elongation_rate_amino_acids_per_s=study.elongation_rate_amino_acids_per_s,
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


@router.get("/studies", response_model=List[OpticalTweezersRibosomeTranslationStudyResponse])
async def list_optical_tweezers_ribosome_translation_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Single-Molecule Optical Tweezers Ribosome Translation Kinetic Polypeptide Translocation Engine studies."""
    repo = OpticalTweezersRibosomeTranslationRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=OpticalTweezersRibosomeTranslationStudyResponse)
async def get_optical_tweezers_ribosome_translation_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Single-Molecule Optical Tweezers Ribosome Translation Kinetic Polypeptide Translocation Engine study by ID."""
    repo = OpticalTweezersRibosomeTranslationRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
