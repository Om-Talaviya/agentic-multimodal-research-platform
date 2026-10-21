"""FastAPI route for Phase 578: Autonomous Xenobiotic Polyethylene Terephthalate (PET) Plastic Enzymatic Depolymerase Engineering & Micro-Solvation Energy Forecaster."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.xenobiotic_pet_depolymerase_repo import XenobioticPetDepolymeraseRepository
from research.orchestration.xenobiotic_pet_depolymerase_engine import XenobioticPetDepolymeraseEngine

router = APIRouter(prefix="/xenobiotic-pet-depolymerase", tags=["Phase 578 - Autonomous Xenobiotic Polyethylene Terephthalate (PET) Plastic Enzymatic Depolymerase Engineering & Micro-Solvation Energy Forecaster"])


class XenobioticPetDepolymeraseAnalyzeRequest(BaseModel):
    name: str = Field(default="Autonomous Xenobiotic PET Plastic Enzymatic Depolymerase Engineering Study")
    target_enzyme: Optional[str] = Field(default="Ideonella sakaiensis PETase Engineered Variant (Fast-PETase/LCC-ICCG)")
    substrate_type: Optional[str] = Field(default="Post-Consumer Highly Crystalline Polyethylene Terephthalate (PET, 35% crystallinity)")
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


class XenobioticPetDepolymeraseStudyResponse(BaseModel):
    id: UUID
    name: str
    target_enzyme: str
    substrate_type: str
    catalytic_efficiency_kcat_km: float
    melting_temperature_tm_celsius: float
    solvation_free_energy_barrier_kcal: float
    depolymerization_yield_percent: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []


@router.post("/analyze", response_model=XenobioticPetDepolymeraseStudyResponse)
async def analyze_xenobiotic_pet_depolymerase(
    req: XenobioticPetDepolymeraseAnalyzeRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Execute autonomous analysis for Autonomous Xenobiotic Polyethylene Terephthalate (PET) Plastic Enzymatic Depolymerase Engineering & Micro-Solvation Energy Forecaster."""
    engine = XenobioticPetDepolymeraseEngine()
    result = engine.analyze(
        target_enzyme=req.target_enzyme,
        substrate_type=req.substrate_type,
        input_scale=req.input_scale,
    )

    repo = XenobioticPetDepolymeraseRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_enzyme=result.target_enzyme,
        substrate_type=result.substrate_type,
        catalytic_efficiency_kcat_km=result.catalytic_efficiency_kcat_km,
        melting_temperature_tm_celsius=result.melting_temperature_tm_celsius,
        solvation_free_energy_barrier_kcal=result.solvation_free_energy_barrier_kcal,
        depolymerization_yield_percent=result.depolymerization_yield_percent,
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

    return XenobioticPetDepolymeraseStudyResponse(
        id=study.id,
        name=study.name,
        target_enzyme=study.target_enzyme,
        substrate_type=study.substrate_type,
        catalytic_efficiency_kcat_km=study.catalytic_efficiency_kcat_km,
        melting_temperature_tm_celsius=study.melting_temperature_tm_celsius,
        solvation_free_energy_barrier_kcal=study.solvation_free_energy_barrier_kcal,
        depolymerization_yield_percent=study.depolymerization_yield_percent,
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


@router.get("/studies", response_model=List[XenobioticPetDepolymeraseStudyResponse])
async def list_xenobiotic_pet_depolymerase_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Xenobiotic Polyethylene Terephthalate (PET) Plastic Enzymatic Depolymerase Engineering studies."""
    repo = XenobioticPetDepolymeraseRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=XenobioticPetDepolymeraseStudyResponse)
async def get_xenobiotic_pet_depolymerase_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Xenobiotic Polyethylene Terephthalate (PET) Plastic Enzymatic Depolymerase Engineering study by ID."""
    repo = XenobioticPetDepolymeraseRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
