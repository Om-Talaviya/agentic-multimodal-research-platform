"""FastAPI routes for Phase 475: Autonomous Multiplexed Bio-Acoustic Cellular Impedance Flow Cytometry Classifier."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.acoustic_impedance_cytometry_repo import AcousticImpedanceCytometryRepository
from research.orchestration.acoustic_impedance_cytometry_engine import AcousticImpedanceCytometryEngine

router = APIRouter(prefix="/acoustic-impedance-cytometry", tags=["acoustic-impedance-cytometry"])


class AnalyzeAcousticImpedanceCytometryRequest(BaseModel):
    name: str = Field(..., example="Autonomous Multiplexed Bio-Acoustic Cellular Impedance Flow Cytometry Classifier Run")
    target_specimen: str = Field(default="High-Throughput Microfluidic Coplanar Electrode Microchannel with Circulating Tumor Cell Suspensions")
    analytical_modality: str = Field(default="acoustic-impedance-cytometry")
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


class AcousticImpedanceCytometryStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    dielectric_membrane_capacitance_uF_per_cm2: float
    cytoplasm_conductivity_S_per_m: float
    acoustic_focusing_transit_time_uniformity_cv: float
    single_cell_classification_accuracy: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=AcousticImpedanceCytometryStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_acoustic_impedance_cytometry(
    req: AnalyzeAcousticImpedanceCytometryRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Multiplexed Bio-Acoustic Cellular Impedance Flow Cytometry Classifier analysis and persist study."""
    engine = AcousticImpedanceCytometryEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = AcousticImpedanceCytometryRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        dielectric_membrane_capacitance_uF_per_cm2=result.dielectric_membrane_capacitance_uF_per_cm2,
        cytoplasm_conductivity_S_per_m=result.cytoplasm_conductivity_S_per_m,
        acoustic_focusing_transit_time_uniformity_cv=result.acoustic_focusing_transit_time_uniformity_cv,
        single_cell_classification_accuracy=result.single_cell_classification_accuracy,
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

    return AcousticImpedanceCytometryStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        dielectric_membrane_capacitance_uF_per_cm2=study.dielectric_membrane_capacitance_uF_per_cm2,
        cytoplasm_conductivity_S_per_m=study.cytoplasm_conductivity_S_per_m,
        acoustic_focusing_transit_time_uniformity_cv=study.acoustic_focusing_transit_time_uniformity_cv,
        single_cell_classification_accuracy=study.single_cell_classification_accuracy,
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


@router.get("/studies", response_model=List[AcousticImpedanceCytometryStudyResponse])
async def list_acoustic_impedance_cytometry_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Multiplexed Bio-Acoustic Cellular Impedance Flow Cytometry Classifier studies."""
    repo = AcousticImpedanceCytometryRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=AcousticImpedanceCytometryStudyResponse)
async def get_acoustic_impedance_cytometry_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Multiplexed Bio-Acoustic Cellular Impedance Flow Cytometry Classifier study by ID."""
    repo = AcousticImpedanceCytometryRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
