"""FastAPI routes for Phase 527: Autonomous Membraneless Coacervate RNA Condensation & Ribozyme Catalytic Acceleration Modeler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.coacervate_nucleic_acid_liquid_condensation_repo import CoacervateNucleicAcidLiquidCondensationRepository
from research.orchestration.coacervate_nucleic_acid_liquid_condensation_engine import CoacervateNucleicAcidLiquidCondensationEngine

router = APIRouter(prefix="/coacervate-nucleic-acid-liquid-condensation", tags=["coacervate-nucleic-acid-liquid-condensation"])


class AnalyzeCoacervateNucleicAcidLiquidCondensationRequest(BaseModel):
    name: str = Field(..., example="Autonomous Membraneless Coacervate RNA Condensation & Ribozyme Catalytic Acceleration Modeler Run")
    target_specimen: str = Field(default="Polycationic Polylysine-Spermidine Complex Coacervate Droplet Encapsulating Hammerhead Ribozymes")
    analytical_modality: str = Field(default="coacervate-rna-condensation")
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


class CoacervateNucleicAcidLiquidCondensationStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    ribozyme_cleavage_rate_enhancement_fold: float
    partition_coefficient_k_partition: float
    droplet_interfacial_surface_tension_uN_m: float
    critical_coacervation_transition_temp_c: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=CoacervateNucleicAcidLiquidCondensationStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_coacervate_nucleic_acid_liquid_condensation(
    req: AnalyzeCoacervateNucleicAcidLiquidCondensationRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Membraneless Coacervate RNA Condensation & Ribozyme Catalytic Acceleration Modeler analysis and persist study."""
    engine = CoacervateNucleicAcidLiquidCondensationEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = CoacervateNucleicAcidLiquidCondensationRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        ribozyme_cleavage_rate_enhancement_fold=result.ribozyme_cleavage_rate_enhancement_fold,
        partition_coefficient_k_partition=result.partition_coefficient_k_partition,
        droplet_interfacial_surface_tension_uN_m=result.droplet_interfacial_surface_tension_uN_m,
        critical_coacervation_transition_temp_c=result.critical_coacervation_transition_temp_c,
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

    return CoacervateNucleicAcidLiquidCondensationStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        ribozyme_cleavage_rate_enhancement_fold=study.ribozyme_cleavage_rate_enhancement_fold,
        partition_coefficient_k_partition=study.partition_coefficient_k_partition,
        droplet_interfacial_surface_tension_uN_m=study.droplet_interfacial_surface_tension_uN_m,
        critical_coacervation_transition_temp_c=study.critical_coacervation_transition_temp_c,
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


@router.get("/studies", response_model=List[CoacervateNucleicAcidLiquidCondensationStudyResponse])
async def list_coacervate_nucleic_acid_liquid_condensation_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Membraneless Coacervate RNA Condensation & Ribozyme Catalytic Acceleration Modeler studies."""
    repo = CoacervateNucleicAcidLiquidCondensationRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=CoacervateNucleicAcidLiquidCondensationStudyResponse)
async def get_coacervate_nucleic_acid_liquid_condensation_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Membraneless Coacervate RNA Condensation & Ribozyme Catalytic Acceleration Modeler study by ID."""
    repo = CoacervateNucleicAcidLiquidCondensationRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
