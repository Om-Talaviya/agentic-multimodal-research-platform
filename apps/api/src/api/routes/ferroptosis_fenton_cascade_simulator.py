"""FastAPI routes for Phase 482: Autonomous Cellular Ferroptosis Lipid Peroxidation Fenton Reaction Cascade Simulator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.ferroptosis_fenton_cascade_simulator_repo import FerroptosisFentonCascadeSimulatorRepository
from research.orchestration.ferroptosis_fenton_cascade_simulator_engine import FerroptosisFentonCascadeSimulatorEngine

router = APIRouter(prefix="/ferroptosis-fenton-cascade-simulator", tags=["ferroptosis-fenton-cascade-simulator"])


class AnalyzeFerroptosisFentonCascadeSimulatorRequest(BaseModel):
    name: str = Field(..., example="Autonomous Cellular Ferroptosis Lipid Peroxidation Fenton Reaction Cascade Simulator Run")
    target_specimen: str = Field(default="GPX4-Inactivated HT-1080 Fibrosarcoma Spheroids with Labile Iron Pool Fe(II) Accumulation")
    analytical_modality: str = Field(default="ferroptosis-fenton-cascade")
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


class FerroptosisFentonCascadeSimulatorStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    lipid_hydroperoxide_accumulation_nmol_mg: float
    labile_iron_pool_chelatable_uM: float
    fenton_reaction_rate_constant_M_inv_s_inv: float
    membrane_permeabilization_lysis_probability: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=FerroptosisFentonCascadeSimulatorStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_ferroptosis_fenton_cascade_simulator(
    req: AnalyzeFerroptosisFentonCascadeSimulatorRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Cellular Ferroptosis Lipid Peroxidation Fenton Reaction Cascade Simulator analysis and persist study."""
    engine = FerroptosisFentonCascadeSimulatorEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = FerroptosisFentonCascadeSimulatorRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        lipid_hydroperoxide_accumulation_nmol_mg=result.lipid_hydroperoxide_accumulation_nmol_mg,
        labile_iron_pool_chelatable_uM=result.labile_iron_pool_chelatable_uM,
        fenton_reaction_rate_constant_M_inv_s_inv=result.fenton_reaction_rate_constant_M_inv_s_inv,
        membrane_permeabilization_lysis_probability=result.membrane_permeabilization_lysis_probability,
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

    return FerroptosisFentonCascadeSimulatorStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        lipid_hydroperoxide_accumulation_nmol_mg=study.lipid_hydroperoxide_accumulation_nmol_mg,
        labile_iron_pool_chelatable_uM=study.labile_iron_pool_chelatable_uM,
        fenton_reaction_rate_constant_M_inv_s_inv=study.fenton_reaction_rate_constant_M_inv_s_inv,
        membrane_permeabilization_lysis_probability=study.membrane_permeabilization_lysis_probability,
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


@router.get("/studies", response_model=List[FerroptosisFentonCascadeSimulatorStudyResponse])
async def list_ferroptosis_fenton_cascade_simulator_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Cellular Ferroptosis Lipid Peroxidation Fenton Reaction Cascade Simulator studies."""
    repo = FerroptosisFentonCascadeSimulatorRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=FerroptosisFentonCascadeSimulatorStudyResponse)
async def get_ferroptosis_fenton_cascade_simulator_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Cellular Ferroptosis Lipid Peroxidation Fenton Reaction Cascade Simulator study by ID."""
    repo = FerroptosisFentonCascadeSimulatorRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
