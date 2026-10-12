"""FastAPI routes for Phase 438: Autonomous Cryo-ET In-Situ Nuclear Pore Complex (NPC) Nuclear Basket Dynamic Conformation Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.cryoet_nuclear_pore_basket_tomography_repo import CryoetNuclearPoreBasketRepository
from research.orchestration.cryoet_nuclear_pore_basket_tomography_engine import CryoetNuclearPoreBasketEngine

router = APIRouter(prefix="/cryoet-nuclear-pore-basket", tags=["cryoet-nuclear-pore-basket"])


class AnalyzeCryoetNuclearPoreBasketRequest(BaseModel):
    name: str = Field(..., example="Autonomous Cryo-ET In-Situ Nuclear Pore Complex (NPC) Nuclear Basket Dynamic Conformation Engine Run")
    target_specimen: str = Field(default="Intact HeLa Cell Nuclear Envelope Vitreous Lamella with 8-Fold NPC Basket")
    analytical_modality: str = Field(default="cryoet-npc-basket")
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


class CryoetNuclearPoreBasketStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    subtomogram_average_resolution_angstrom: float
    basket_dilation_radius_nm: float
    fg_nucleoporin_confinement_entropy: float
    transport_receptor_docking_occupancy: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=CryoetNuclearPoreBasketStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_cryoet_nuclear_pore_basket_tomography(
    req: AnalyzeCryoetNuclearPoreBasketRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Cryo-ET In-Situ Nuclear Pore Complex (NPC) Nuclear Basket Dynamic Conformation Engine analysis and persist study."""
    engine = CryoetNuclearPoreBasketEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = CryoetNuclearPoreBasketRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        subtomogram_average_resolution_angstrom=result.subtomogram_average_resolution_angstrom,
        basket_dilation_radius_nm=result.basket_dilation_radius_nm,
        fg_nucleoporin_confinement_entropy=result.fg_nucleoporin_confinement_entropy,
        transport_receptor_docking_occupancy=result.transport_receptor_docking_occupancy,
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

    return CryoetNuclearPoreBasketStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        subtomogram_average_resolution_angstrom=study.subtomogram_average_resolution_angstrom,
        basket_dilation_radius_nm=study.basket_dilation_radius_nm,
        fg_nucleoporin_confinement_entropy=study.fg_nucleoporin_confinement_entropy,
        transport_receptor_docking_occupancy=study.transport_receptor_docking_occupancy,
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


@router.get("/studies", response_model=List[CryoetNuclearPoreBasketStudyResponse])
async def list_cryoet_nuclear_pore_basket_tomography_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Cryo-ET In-Situ Nuclear Pore Complex (NPC) Nuclear Basket Dynamic Conformation Engine studies."""
    repo = CryoetNuclearPoreBasketRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=CryoetNuclearPoreBasketStudyResponse)
async def get_cryoet_nuclear_pore_basket_tomography_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Cryo-ET In-Situ Nuclear Pore Complex (NPC) Nuclear Basket Dynamic Conformation Engine study by ID."""
    repo = CryoetNuclearPoreBasketRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
