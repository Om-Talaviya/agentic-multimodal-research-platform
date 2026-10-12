"""FastAPI routes for Phase 443: Autonomous Cellular Senescence-Associated Secretory Phenotype (SASP) Paracrine Spreading & Tissue Exhaustion Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.cellular_senescence_sasp_paracrine_spreading_repo import CellularSenescenceSaspRepository
from research.orchestration.cellular_senescence_sasp_paracrine_spreading_engine import CellularSenescenceSaspEngine

router = APIRouter(prefix="/cellular-senescence-sasp", tags=["cellular-senescence-sasp"])


class AnalyzeCellularSenescenceSaspRequest(BaseModel):
    name: str = Field(..., example="Autonomous Cellular Senescence-Associated Secretory Phenotype (SASP) Paracrine Spreading & Tissue Exhaustion Engine Run")
    target_specimen: str = Field(default="Replicative Senescent Human Dermal Fibroblasts in 3D Collagen Microtissue with Bystander Cells")
    analytical_modality: str = Field(default="senescence-sasp-spreading")
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


class CellularSenescenceSaspStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    sasp_paracrine_diffusion_radius_um: float
    p16_ink4a_induction_fold_change: float
    bystander_senescence_induction_rate: float
    senolytic_depletion_efficacy_score: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=CellularSenescenceSaspStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_cellular_senescence_sasp_paracrine_spreading(
    req: AnalyzeCellularSenescenceSaspRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Cellular Senescence-Associated Secretory Phenotype (SASP) Paracrine Spreading & Tissue Exhaustion Engine analysis and persist study."""
    engine = CellularSenescenceSaspEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = CellularSenescenceSaspRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        sasp_paracrine_diffusion_radius_um=result.sasp_paracrine_diffusion_radius_um,
        p16_ink4a_induction_fold_change=result.p16_ink4a_induction_fold_change,
        bystander_senescence_induction_rate=result.bystander_senescence_induction_rate,
        senolytic_depletion_efficacy_score=result.senolytic_depletion_efficacy_score,
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

    return CellularSenescenceSaspStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        sasp_paracrine_diffusion_radius_um=study.sasp_paracrine_diffusion_radius_um,
        p16_ink4a_induction_fold_change=study.p16_ink4a_induction_fold_change,
        bystander_senescence_induction_rate=study.bystander_senescence_induction_rate,
        senolytic_depletion_efficacy_score=study.senolytic_depletion_efficacy_score,
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


@router.get("/studies", response_model=List[CellularSenescenceSaspStudyResponse])
async def list_cellular_senescence_sasp_paracrine_spreading_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Cellular Senescence-Associated Secretory Phenotype (SASP) Paracrine Spreading & Tissue Exhaustion Engine studies."""
    repo = CellularSenescenceSaspRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=CellularSenescenceSaspStudyResponse)
async def get_cellular_senescence_sasp_paracrine_spreading_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Cellular Senescence-Associated Secretory Phenotype (SASP) Paracrine Spreading & Tissue Exhaustion Engine study by ID."""
    repo = CellularSenescenceSaspRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
