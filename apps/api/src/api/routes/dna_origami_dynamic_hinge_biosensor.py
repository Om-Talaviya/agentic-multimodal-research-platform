"""FastAPI routes for Phase 435: Autonomous Reconfigurable DNA Origami Dynamic Hinge Compliant Nano-Actuator Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.dna_origami_dynamic_hinge_biosensor_repo import DnaOrigamiDynamicHingeRepository
from research.orchestration.dna_origami_dynamic_hinge_biosensor_engine import DnaOrigamiDynamicHingeEngine

router = APIRouter(prefix="/dna-origami-dynamic-hinge", tags=["dna-origami-dynamic-hinge"])


class AnalyzeDnaOrigamiDynamicHingeRequest(BaseModel):
    name: str = Field(..., example="Autonomous Reconfigurable DNA Origami Dynamic Hinge Compliant Nano-Actuator Engine Run")
    target_specimen: str = Field(default="Hexagonal Bundle DNA Origami Nano-Hinge with Fluorophore/Quencher FRET Pair")
    analytical_modality: str = Field(default="dna-origami-hinge")
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


class DnaOrigamiDynamicHingeStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    hinge_flexibility_angle_deg: float
    fret_efficiency_dynamic_ratio: float
    folding_yield_percentage: float
    magnesium_stabilization_mM: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=DnaOrigamiDynamicHingeStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_dna_origami_dynamic_hinge_biosensor(
    req: AnalyzeDnaOrigamiDynamicHingeRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Reconfigurable DNA Origami Dynamic Hinge Compliant Nano-Actuator Engine analysis and persist study."""
    engine = DnaOrigamiDynamicHingeEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = DnaOrigamiDynamicHingeRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        hinge_flexibility_angle_deg=result.hinge_flexibility_angle_deg,
        fret_efficiency_dynamic_ratio=result.fret_efficiency_dynamic_ratio,
        folding_yield_percentage=result.folding_yield_percentage,
        magnesium_stabilization_mM=result.magnesium_stabilization_mM,
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

    return DnaOrigamiDynamicHingeStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        hinge_flexibility_angle_deg=study.hinge_flexibility_angle_deg,
        fret_efficiency_dynamic_ratio=study.fret_efficiency_dynamic_ratio,
        folding_yield_percentage=study.folding_yield_percentage,
        magnesium_stabilization_mM=study.magnesium_stabilization_mM,
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


@router.get("/studies", response_model=List[DnaOrigamiDynamicHingeStudyResponse])
async def list_dna_origami_dynamic_hinge_biosensor_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Reconfigurable DNA Origami Dynamic Hinge Compliant Nano-Actuator Engine studies."""
    repo = DnaOrigamiDynamicHingeRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=DnaOrigamiDynamicHingeStudyResponse)
async def get_dna_origami_dynamic_hinge_biosensor_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Reconfigurable DNA Origami Dynamic Hinge Compliant Nano-Actuator Engine study by ID."""
    repo = DnaOrigamiDynamicHingeRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
