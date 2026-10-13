"""FastAPI routes for Phase 458: Autonomous Organ-on-Chip Multi-Tissue Microvascular Fluid Shear Stress Perfusion Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.organ_on_chip_microvascular_shear_repo import OrganOnChipMicrovascularShearRepository
from research.orchestration.organ_on_chip_microvascular_shear_engine import OrganOnChipMicrovascularShearEngine

router = APIRouter(prefix="/organ-on-chip-microvascular-shear", tags=["organ-on-chip-microvascular-shear"])


class AnalyzeOrganOnChipMicrovascularShearRequest(BaseModel):
    name: str = Field(..., example="Autonomous Organ-on-Chip Multi-Tissue Microvascular Fluid Shear Stress Perfusion Engine Run")
    target_specimen: str = Field(default="Dual-Channel Microfluidic Blood-Brain Barrier Chip with Pericytes and Endothelial Shear")
    analytical_modality: str = Field(default="microvascular-fluid-shear")
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


class OrganOnChipMicrovascularShearStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    wall_shear_stress_dynes_per_cm2: float
    transendothelial_electrical_resistance_teer_ohm_cm2: float
    dextran_permeability_coefficient_cm_per_s: float
    endothelial_alignment_angle_std_deg: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=OrganOnChipMicrovascularShearStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_organ_on_chip_microvascular_shear(
    req: AnalyzeOrganOnChipMicrovascularShearRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Organ-on-Chip Multi-Tissue Microvascular Fluid Shear Stress Perfusion Engine analysis and persist study."""
    engine = OrganOnChipMicrovascularShearEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = OrganOnChipMicrovascularShearRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        wall_shear_stress_dynes_per_cm2=result.wall_shear_stress_dynes_per_cm2,
        transendothelial_electrical_resistance_teer_ohm_cm2=result.transendothelial_electrical_resistance_teer_ohm_cm2,
        dextran_permeability_coefficient_cm_per_s=result.dextran_permeability_coefficient_cm_per_s,
        endothelial_alignment_angle_std_deg=result.endothelial_alignment_angle_std_deg,
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

    return OrganOnChipMicrovascularShearStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        wall_shear_stress_dynes_per_cm2=study.wall_shear_stress_dynes_per_cm2,
        transendothelial_electrical_resistance_teer_ohm_cm2=study.transendothelial_electrical_resistance_teer_ohm_cm2,
        dextran_permeability_coefficient_cm_per_s=study.dextran_permeability_coefficient_cm_per_s,
        endothelial_alignment_angle_std_deg=study.endothelial_alignment_angle_std_deg,
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


@router.get("/studies", response_model=List[OrganOnChipMicrovascularShearStudyResponse])
async def list_organ_on_chip_microvascular_shear_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Organ-on-Chip Multi-Tissue Microvascular Fluid Shear Stress Perfusion Engine studies."""
    repo = OrganOnChipMicrovascularShearRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=OrganOnChipMicrovascularShearStudyResponse)
async def get_organ_on_chip_microvascular_shear_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Organ-on-Chip Multi-Tissue Microvascular Fluid Shear Stress Perfusion Engine study by ID."""
    repo = OrganOnChipMicrovascularShearRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
