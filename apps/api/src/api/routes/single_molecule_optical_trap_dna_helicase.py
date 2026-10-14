"""FastAPI routes for Phase 512: Autonomous Single-Molecule Dual-Trap Optical Tweezers DNA Helicase Unwinding Stepper."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.single_molecule_optical_trap_dna_helicase_repo import SingleMoleculeOpticalTrapDnaHelicaseRepository
from research.orchestration.single_molecule_optical_trap_dna_helicase_engine import SingleMoleculeOpticalTrapDnaHelicaseEngine

router = APIRouter(prefix="/single-molecule-optical-trap-dna-helicase", tags=["single-molecule-optical-trap-dna-helicase"])


class AnalyzeSingleMoleculeOpticalTrapDnaHelicaseRequest(BaseModel):
    name: str = Field(..., example="Autonomous Single-Molecule Dual-Trap Optical Tweezers DNA Helicase Unwinding Stepper Run")
    target_specimen: str = Field(default="Dual-Beam Optical Trap Tethered dsDNA Hairpin with Recombinant Human Bloom Syndrome Helicase")
    analytical_modality: str = Field(default="optical-trap-helicase-unwinding")
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


class SingleMoleculeOpticalTrapDnaHelicaseStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    helicase_stepping_velocity_bp_per_s: float
    atp_fuel_efficiency_bp_per_atp: float
    strand_unwinding_processivity_bp: float
    sub_nanometer_step_size_bp: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=SingleMoleculeOpticalTrapDnaHelicaseStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_single_molecule_optical_trap_dna_helicase(
    req: AnalyzeSingleMoleculeOpticalTrapDnaHelicaseRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Single-Molecule Dual-Trap Optical Tweezers DNA Helicase Unwinding Stepper analysis and persist study."""
    engine = SingleMoleculeOpticalTrapDnaHelicaseEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SingleMoleculeOpticalTrapDnaHelicaseRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        helicase_stepping_velocity_bp_per_s=result.helicase_stepping_velocity_bp_per_s,
        atp_fuel_efficiency_bp_per_atp=result.atp_fuel_efficiency_bp_per_atp,
        strand_unwinding_processivity_bp=result.strand_unwinding_processivity_bp,
        sub_nanometer_step_size_bp=result.sub_nanometer_step_size_bp,
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

    return SingleMoleculeOpticalTrapDnaHelicaseStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        helicase_stepping_velocity_bp_per_s=study.helicase_stepping_velocity_bp_per_s,
        atp_fuel_efficiency_bp_per_atp=study.atp_fuel_efficiency_bp_per_atp,
        strand_unwinding_processivity_bp=study.strand_unwinding_processivity_bp,
        sub_nanometer_step_size_bp=study.sub_nanometer_step_size_bp,
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


@router.get("/studies", response_model=List[SingleMoleculeOpticalTrapDnaHelicaseStudyResponse])
async def list_single_molecule_optical_trap_dna_helicase_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Single-Molecule Dual-Trap Optical Tweezers DNA Helicase Unwinding Stepper studies."""
    repo = SingleMoleculeOpticalTrapDnaHelicaseRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SingleMoleculeOpticalTrapDnaHelicaseStudyResponse)
async def get_single_molecule_optical_trap_dna_helicase_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Single-Molecule Dual-Trap Optical Tweezers DNA Helicase Unwinding Stepper study by ID."""
    repo = SingleMoleculeOpticalTrapDnaHelicaseRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
