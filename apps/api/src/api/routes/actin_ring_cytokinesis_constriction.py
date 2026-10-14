"""FastAPI routes for Phase 477: Autonomous Nanoscale Cytoskeletal Actin Ring Constriction & Cytokinesis Cleavage Furrow Modeler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.actin_ring_cytokinesis_constriction_repo import ActinRingCytokinesisConstrictionRepository
from research.orchestration.actin_ring_cytokinesis_constriction_engine import ActinRingCytokinesisConstrictionEngine

router = APIRouter(prefix="/actin-ring-cytokinesis-constriction", tags=["actin-ring-cytokinesis-constriction"])


class AnalyzeActinRingCytokinesisConstrictionRequest(BaseModel):
    name: str = Field(..., example="Autonomous Nanoscale Cytoskeletal Actin Ring Constriction & Cytokinesis Cleavage Furrow Modeler Run")
    target_specimen: str = Field(default="Vitrified Dividing S. pombe Protoplast Actomyosin Ring Complex with Myosin-II / Formin Cdc12 Clusters")
    analytical_modality: str = Field(default="actin-ring-cytokinesis-constriction")
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


class ActinRingCytokinesisConstrictionStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    contractile_ring_tension_pN: float
    furrow_ingression_velocity_nm_per_s: float
    actin_filament_turnover_rate_s_inv: float
    ring_diameter_constriction_ratio: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=ActinRingCytokinesisConstrictionStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_actin_ring_cytokinesis_constriction(
    req: AnalyzeActinRingCytokinesisConstrictionRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Nanoscale Cytoskeletal Actin Ring Constriction & Cytokinesis Cleavage Furrow Modeler analysis and persist study."""
    engine = ActinRingCytokinesisConstrictionEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = ActinRingCytokinesisConstrictionRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        contractile_ring_tension_pN=result.contractile_ring_tension_pN,
        furrow_ingression_velocity_nm_per_s=result.furrow_ingression_velocity_nm_per_s,
        actin_filament_turnover_rate_s_inv=result.actin_filament_turnover_rate_s_inv,
        ring_diameter_constriction_ratio=result.ring_diameter_constriction_ratio,
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

    return ActinRingCytokinesisConstrictionStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        contractile_ring_tension_pN=study.contractile_ring_tension_pN,
        furrow_ingression_velocity_nm_per_s=study.furrow_ingression_velocity_nm_per_s,
        actin_filament_turnover_rate_s_inv=study.actin_filament_turnover_rate_s_inv,
        ring_diameter_constriction_ratio=study.ring_diameter_constriction_ratio,
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


@router.get("/studies", response_model=List[ActinRingCytokinesisConstrictionStudyResponse])
async def list_actin_ring_cytokinesis_constriction_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Nanoscale Cytoskeletal Actin Ring Constriction & Cytokinesis Cleavage Furrow Modeler studies."""
    repo = ActinRingCytokinesisConstrictionRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=ActinRingCytokinesisConstrictionStudyResponse)
async def get_actin_ring_cytokinesis_constriction_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Nanoscale Cytoskeletal Actin Ring Constriction & Cytokinesis Cleavage Furrow Modeler study by ID."""
    repo = ActinRingCytokinesisConstrictionRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
