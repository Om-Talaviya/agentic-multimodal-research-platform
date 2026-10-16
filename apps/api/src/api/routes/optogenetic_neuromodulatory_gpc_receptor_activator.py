"""FastAPI route for Phase 572: Autonomous Optogenetic G-Protein-Coupled Receptor (Opto-GPCR) Spatiotemporal Second Messenger Signaling Predictor."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.optogenetic_neuromodulatory_gpc_receptor_activator_repo import OptogeneticNeuromodulatoryGpcReceptorActivatorRepository
from research.orchestration.optogenetic_neuromodulatory_gpc_receptor_activator_engine import OptogeneticNeuromodulatoryGpcReceptorActivatorEngine

router = APIRouter(prefix="/optogenetic-neuromodulatory-gpc-receptor-activator", tags=["Phase 572 - Autonomous Optogenetic G-Protein-Coupled Receptor (Opto-GPCR) Spatiotemporal Second Messenger Signaling Predictor"])


class OptogeneticNeuromodulatoryGpcReceptorActivatorAnalyzeRequest(BaseModel):
    name: str = Field(default="Autonomous Optogenetic G-Protein-Coupled Receptor (Opto-GPCR) Spatiotemporal Second Messenger Signaling Predictor Study")
    target_specimen: Optional[str] = Field(default="Opto-beta2-Adrenergic Receptor Chimeric Constructs Expressed in Primary Hippocampal Neurons")
    analytical_modality: Optional[str] = Field(default="opto-gpcr-second-messenger-modeling")
    input_scale: float = Field(default=1.0, ge=0.1, le=10.0)


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


class OptogeneticNeuromodulatoryGpcReceptorActivatorStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    camp_generation_rate_nm_s: float
    g_protein_coupling_selectivity: float
    photocurrent_deactivation_tau_ms: float
    downstream_phosphorylation_index: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []


@router.post("/analyze", response_model=OptogeneticNeuromodulatoryGpcReceptorActivatorStudyResponse)
async def analyze_optogenetic_neuromodulatory_gpc_receptor_activator(
    req: OptogeneticNeuromodulatoryGpcReceptorActivatorAnalyzeRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Execute autonomous analysis for Autonomous Optogenetic G-Protein-Coupled Receptor (Opto-GPCR) Spatiotemporal Second Messenger Signaling Predictor."""
    engine = OptogeneticNeuromodulatoryGpcReceptorActivatorEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = OptogeneticNeuromodulatoryGpcReceptorActivatorRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        camp_generation_rate_nm_s=result.camp_generation_rate_nm_s,
        g_protein_coupling_selectivity=result.g_protein_coupling_selectivity,
        photocurrent_deactivation_tau_ms=result.photocurrent_deactivation_tau_ms,
        downstream_phosphorylation_index=result.downstream_phosphorylation_index,
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

    return OptogeneticNeuromodulatoryGpcReceptorActivatorStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        camp_generation_rate_nm_s=study.camp_generation_rate_nm_s,
        g_protein_coupling_selectivity=study.g_protein_coupling_selectivity,
        photocurrent_deactivation_tau_ms=study.photocurrent_deactivation_tau_ms,
        downstream_phosphorylation_index=study.downstream_phosphorylation_index,
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


@router.get("/studies", response_model=List[OptogeneticNeuromodulatoryGpcReceptorActivatorStudyResponse])
async def list_optogenetic_neuromodulatory_gpc_receptor_activator_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Optogenetic G-Protein-Coupled Receptor (Opto-GPCR) Spatiotemporal Second Messenger Signaling Predictor studies."""
    repo = OptogeneticNeuromodulatoryGpcReceptorActivatorRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=OptogeneticNeuromodulatoryGpcReceptorActivatorStudyResponse)
async def get_optogenetic_neuromodulatory_gpc_receptor_activator_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Optogenetic G-Protein-Coupled Receptor (Opto-GPCR) Spatiotemporal Second Messenger Signaling Predictor study by ID."""
    repo = OptogeneticNeuromodulatoryGpcReceptorActivatorRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
