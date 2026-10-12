"""FastAPI routes for Phase 422: Autonomous Allosteric Ligand Residence Time & Dissociation Rate Constant (k_off) Molecular Dynamics Extractor."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.ligand_residence_time_koff_repo import LigandResidenceTimeKoffRepository
from research.orchestration.ligand_residence_time_koff_engine import LigandResidenceTimeKoffEngine

router = APIRouter(prefix="/ligand-residence-time-koff", tags=["ligand-residence-time-koff"])


class AnalyzeLigandResidenceTimeKoffRequest(BaseModel):
    name: str = Field(..., example="Autonomous Allosteric Ligand Residence Time & Dissociation Rate Constant (k_off) Molecular Dynamics Extractor Run")
    target_specimen: str = Field(default="Kinase Allosteric Pocket with Type II Small Molecule Inhibitor")
    analytical_modality: str = Field(default="residence-time-koff")
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


class LigandResidenceTimeKoffStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    unbinding_rate_koff_s_inv: float
    residence_time_minutes: float
    dissociation_free_energy_barrier_kcal: float
    binding_pocket_hydration_entropy: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=LigandResidenceTimeKoffStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_ligand_residence_time_koff(
    req: AnalyzeLigandResidenceTimeKoffRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Allosteric Ligand Residence Time & Dissociation Rate Constant (k_off) Molecular Dynamics Extractor analysis and persist study."""
    engine = LigandResidenceTimeKoffEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = LigandResidenceTimeKoffRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        unbinding_rate_koff_s_inv=result.unbinding_rate_koff_s_inv,
        residence_time_minutes=result.residence_time_minutes,
        dissociation_free_energy_barrier_kcal=result.dissociation_free_energy_barrier_kcal,
        binding_pocket_hydration_entropy=result.binding_pocket_hydration_entropy,
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

    return LigandResidenceTimeKoffStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        unbinding_rate_koff_s_inv=study.unbinding_rate_koff_s_inv,
        residence_time_minutes=study.residence_time_minutes,
        dissociation_free_energy_barrier_kcal=study.dissociation_free_energy_barrier_kcal,
        binding_pocket_hydration_entropy=study.binding_pocket_hydration_entropy,
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


@router.get("/studies", response_model=List[LigandResidenceTimeKoffStudyResponse])
async def list_ligand_residence_time_koff_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Allosteric Ligand Residence Time & Dissociation Rate Constant (k_off) Molecular Dynamics Extractor studies."""
    repo = LigandResidenceTimeKoffRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=LigandResidenceTimeKoffStudyResponse)
async def get_ligand_residence_time_koff_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Allosteric Ligand Residence Time & Dissociation Rate Constant (k_off) Molecular Dynamics Extractor study by ID."""
    repo = LigandResidenceTimeKoffRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
