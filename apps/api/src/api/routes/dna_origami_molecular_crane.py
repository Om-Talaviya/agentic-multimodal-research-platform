"""FastAPI routes for Phase 483: Autonomous DNA Origami Molecular Crane Nanomechanical Arm & Rotational Stepper Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.dna_origami_molecular_crane_repo import DnaOrigamiMolecularCraneRepository
from research.orchestration.dna_origami_molecular_crane_engine import DnaOrigamiMolecularCraneEngine

router = APIRouter(prefix="/dna-origami-molecular-crane", tags=["dna-origami-molecular-crane"])


class AnalyzeDnaOrigamiMolecularCraneRequest(BaseModel):
    name: str = Field(..., example="Autonomous DNA Origami Molecular Crane Nanomechanical Arm & Rotational Stepper Engine Run")
    target_specimen: str = Field(default="3D Scaffolded DNA Origami Mechanical Crane with Light-Responsive Azobenzene Rotational Actuator")
    analytical_modality: str = Field(default="dna-origami-crane-mechanics")
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


class DnaOrigamiMolecularCraneStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    crane_arm_rotational_angle_degrees: float
    rotational_step_precision_std_deg: float
    nanomechanical_work_output_kbT: float
    structural_rigidity_persistence_length_nm: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=DnaOrigamiMolecularCraneStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_dna_origami_molecular_crane(
    req: AnalyzeDnaOrigamiMolecularCraneRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous DNA Origami Molecular Crane Nanomechanical Arm & Rotational Stepper Engine analysis and persist study."""
    engine = DnaOrigamiMolecularCraneEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = DnaOrigamiMolecularCraneRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        crane_arm_rotational_angle_degrees=result.crane_arm_rotational_angle_degrees,
        rotational_step_precision_std_deg=result.rotational_step_precision_std_deg,
        nanomechanical_work_output_kbT=result.nanomechanical_work_output_kbT,
        structural_rigidity_persistence_length_nm=result.structural_rigidity_persistence_length_nm,
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

    return DnaOrigamiMolecularCraneStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        crane_arm_rotational_angle_degrees=study.crane_arm_rotational_angle_degrees,
        rotational_step_precision_std_deg=study.rotational_step_precision_std_deg,
        nanomechanical_work_output_kbT=study.nanomechanical_work_output_kbT,
        structural_rigidity_persistence_length_nm=study.structural_rigidity_persistence_length_nm,
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


@router.get("/studies", response_model=List[DnaOrigamiMolecularCraneStudyResponse])
async def list_dna_origami_molecular_crane_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous DNA Origami Molecular Crane Nanomechanical Arm & Rotational Stepper Engine studies."""
    repo = DnaOrigamiMolecularCraneRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=DnaOrigamiMolecularCraneStudyResponse)
async def get_dna_origami_molecular_crane_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous DNA Origami Molecular Crane Nanomechanical Arm & Rotational Stepper Engine study by ID."""
    repo = DnaOrigamiMolecularCraneRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
