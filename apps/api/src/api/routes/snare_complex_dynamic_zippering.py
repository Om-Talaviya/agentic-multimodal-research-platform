"""FastAPI routes for Phase 487: Autonomous Synaptic Vesicle SNARE Complex Dynamic Zippering & Neurotransmitter Release Predictor."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.snare_complex_dynamic_zippering_repo import SnareComplexDynamicZipperingRepository
from research.orchestration.snare_complex_dynamic_zippering_engine import SnareComplexDynamicZipperingEngine

router = APIRouter(prefix="/snare-complex-dynamic-zippering", tags=["snare-complex-dynamic-zippering"])


class AnalyzeSnareComplexDynamicZipperingRequest(BaseModel):
    name: str = Field(..., example="Autonomous Synaptic Vesicle SNARE Complex Dynamic Zippering & Neurotransmitter Release Predictor Run")
    target_specimen: str = Field(default="Reconstituted Proteoliposome Single-Vesicle Synaptobrevin-2 / Syntaxin-1A / SNAP-25 Assembly")
    analytical_modality: str = Field(default="snare-complex-zippering")
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


class SnareComplexDynamicZipperingStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    snare_zippering_free_energy_kbT: float
    membrane_fusion_pore_opening_time_ms: float
    synaptotagmin_ca2_activation_threshold_uM: float
    vesicle_docking_priming_probability: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=SnareComplexDynamicZipperingStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_snare_complex_dynamic_zippering(
    req: AnalyzeSnareComplexDynamicZipperingRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Synaptic Vesicle SNARE Complex Dynamic Zippering & Neurotransmitter Release Predictor analysis and persist study."""
    engine = SnareComplexDynamicZipperingEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SnareComplexDynamicZipperingRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        snare_zippering_free_energy_kbT=result.snare_zippering_free_energy_kbT,
        membrane_fusion_pore_opening_time_ms=result.membrane_fusion_pore_opening_time_ms,
        synaptotagmin_ca2_activation_threshold_uM=result.synaptotagmin_ca2_activation_threshold_uM,
        vesicle_docking_priming_probability=result.vesicle_docking_priming_probability,
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

    return SnareComplexDynamicZipperingStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        snare_zippering_free_energy_kbT=study.snare_zippering_free_energy_kbT,
        membrane_fusion_pore_opening_time_ms=study.membrane_fusion_pore_opening_time_ms,
        synaptotagmin_ca2_activation_threshold_uM=study.synaptotagmin_ca2_activation_threshold_uM,
        vesicle_docking_priming_probability=study.vesicle_docking_priming_probability,
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


@router.get("/studies", response_model=List[SnareComplexDynamicZipperingStudyResponse])
async def list_snare_complex_dynamic_zippering_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Synaptic Vesicle SNARE Complex Dynamic Zippering & Neurotransmitter Release Predictor studies."""
    repo = SnareComplexDynamicZipperingRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SnareComplexDynamicZipperingStudyResponse)
async def get_snare_complex_dynamic_zippering_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Synaptic Vesicle SNARE Complex Dynamic Zippering & Neurotransmitter Release Predictor study by ID."""
    repo = SnareComplexDynamicZipperingRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
