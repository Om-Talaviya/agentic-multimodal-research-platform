"""FastAPI routes for Phase 485: Autonomous Bacterial Quorum Quenching Enzymatic Lactonase Biofilm Dispersion Forecaster."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.quorum_quenching_lactonase_dispersion_repo import QuorumQuenchingLactonaseDispersionRepository
from research.orchestration.quorum_quenching_lactonase_dispersion_engine import QuorumQuenchingLactonaseDispersionEngine

router = APIRouter(prefix="/quorum-quenching-lactonase-dispersion", tags=["quorum-quenching-lactonase-dispersion"])


class AnalyzeQuorumQuenchingLactonaseDispersionRequest(BaseModel):
    name: str = Field(..., example="Autonomous Bacterial Quorum Quenching Enzymatic Lactonase Biofilm Dispersion Forecaster Run")
    target_specimen: str = Field(default="Pseudomonas aeruginosa PAO1 Mature Biofilm with Immobilized Phosphotriesterase-Like Lactonase (PLL)")
    analytical_modality: str = Field(default="quorum-quenching-lactonase")
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


class QuorumQuenchingLactonaseDispersionStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    ahl_hydrolysis_kcat_over_km_M_inv_s_inv: float
    biofilm_extracellular_matrix_reduction_pct: float
    quorum_regulated_pyocyanin_suppression_pct: float
    antibiotic_potency_synergy_fold_increase: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=QuorumQuenchingLactonaseDispersionStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_quorum_quenching_lactonase_dispersion(
    req: AnalyzeQuorumQuenchingLactonaseDispersionRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Bacterial Quorum Quenching Enzymatic Lactonase Biofilm Dispersion Forecaster analysis and persist study."""
    engine = QuorumQuenchingLactonaseDispersionEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = QuorumQuenchingLactonaseDispersionRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        ahl_hydrolysis_kcat_over_km_M_inv_s_inv=result.ahl_hydrolysis_kcat_over_km_M_inv_s_inv,
        biofilm_extracellular_matrix_reduction_pct=result.biofilm_extracellular_matrix_reduction_pct,
        quorum_regulated_pyocyanin_suppression_pct=result.quorum_regulated_pyocyanin_suppression_pct,
        antibiotic_potency_synergy_fold_increase=result.antibiotic_potency_synergy_fold_increase,
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

    return QuorumQuenchingLactonaseDispersionStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        ahl_hydrolysis_kcat_over_km_M_inv_s_inv=study.ahl_hydrolysis_kcat_over_km_M_inv_s_inv,
        biofilm_extracellular_matrix_reduction_pct=study.biofilm_extracellular_matrix_reduction_pct,
        quorum_regulated_pyocyanin_suppression_pct=study.quorum_regulated_pyocyanin_suppression_pct,
        antibiotic_potency_synergy_fold_increase=study.antibiotic_potency_synergy_fold_increase,
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


@router.get("/studies", response_model=List[QuorumQuenchingLactonaseDispersionStudyResponse])
async def list_quorum_quenching_lactonase_dispersion_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Bacterial Quorum Quenching Enzymatic Lactonase Biofilm Dispersion Forecaster studies."""
    repo = QuorumQuenchingLactonaseDispersionRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=QuorumQuenchingLactonaseDispersionStudyResponse)
async def get_quorum_quenching_lactonase_dispersion_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Bacterial Quorum Quenching Enzymatic Lactonase Biofilm Dispersion Forecaster study by ID."""
    repo = QuorumQuenchingLactonaseDispersionRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
