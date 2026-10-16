"""FastAPI routes for Phase 552: Autonomous Deep Learning De Novo Ribosome Binding Site (RBS) Translation Initiation Rate Optimizer."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.denovo_rbs_translation_initiation_optimizer_repo import DenovoRbsTranslationInitiationOptimizerRepository
from research.orchestration.denovo_rbs_translation_initiation_optimizer_engine import DenovoRbsTranslationInitiationOptimizerEngine

router = APIRouter(prefix="/denovo-rbs-translation-initiation-optimizer", tags=["denovo-rbs-translation-initiation-optimizer"])


class AnalyzeDenovoRbsTranslationInitiationOptimizerRequest(BaseModel):
    name: str = Field(..., example="Autonomous Deep Learning De Novo Ribosome Binding Site (RBS) Translation Initiation Rate Optimizer Run")
    target_specimen: str = Field(default="Synthetic mRNA Polycistronic Operon 5' UTR Shine-Dalgarno Core Library in Escherichia coli BL21(DE3)")
    analytical_modality: str = Field(default="de-novo-rbs-optimization")
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


class DenovoRbsTranslationInitiationOptimizerStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    translation_initiation_rate_arbitrary_units: float
    rna_secondary_structure_free_energy_kcal_mol: float
    shine_dalgarno_16s_rrna_hybridization_energy: float
    cross_cistronic_translational_coupling_ratio: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=DenovoRbsTranslationInitiationOptimizerStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_denovo_rbs_translation_initiation_optimizer(
    req: AnalyzeDenovoRbsTranslationInitiationOptimizerRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Deep Learning De Novo Ribosome Binding Site (RBS) Translation Initiation Rate Optimizer analysis and persist study."""
    engine = DenovoRbsTranslationInitiationOptimizerEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = DenovoRbsTranslationInitiationOptimizerRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        translation_initiation_rate_arbitrary_units=result.translation_initiation_rate_arbitrary_units,
        rna_secondary_structure_free_energy_kcal_mol=result.rna_secondary_structure_free_energy_kcal_mol,
        shine_dalgarno_16s_rrna_hybridization_energy=result.shine_dalgarno_16s_rrna_hybridization_energy,
        cross_cistronic_translational_coupling_ratio=result.cross_cistronic_translational_coupling_ratio,
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

    return DenovoRbsTranslationInitiationOptimizerStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        translation_initiation_rate_arbitrary_units=study.translation_initiation_rate_arbitrary_units,
        rna_secondary_structure_free_energy_kcal_mol=study.rna_secondary_structure_free_energy_kcal_mol,
        shine_dalgarno_16s_rrna_hybridization_energy=study.shine_dalgarno_16s_rrna_hybridization_energy,
        cross_cistronic_translational_coupling_ratio=study.cross_cistronic_translational_coupling_ratio,
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


@router.get("/studies", response_model=List[DenovoRbsTranslationInitiationOptimizerStudyResponse])
async def list_denovo_rbs_translation_initiation_optimizer_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Deep Learning De Novo Ribosome Binding Site (RBS) Translation Initiation Rate Optimizer studies."""
    repo = DenovoRbsTranslationInitiationOptimizerRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=DenovoRbsTranslationInitiationOptimizerStudyResponse)
async def get_denovo_rbs_translation_initiation_optimizer_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Deep Learning De Novo Ribosome Binding Site (RBS) Translation Initiation Rate Optimizer study by ID."""
    repo = DenovoRbsTranslationInitiationOptimizerRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
