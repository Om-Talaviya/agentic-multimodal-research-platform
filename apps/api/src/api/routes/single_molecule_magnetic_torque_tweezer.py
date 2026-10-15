"""FastAPI routes for Phase 537: Autonomous Single-Molecule Magnetic Torque Tweezers (MTT) DNA Supercoiling & Twist Modeler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.single_molecule_magnetic_torque_tweezer_repo import SingleMoleculeMagneticTorqueTweezerRepository
from research.orchestration.single_molecule_magnetic_torque_tweezer_engine import SingleMoleculeMagneticTorqueTweezerEngine

router = APIRouter(prefix="/single-molecule-magnetic-torque-tweezer", tags=["single-molecule-magnetic-torque-tweezer"])


class AnalyzeSingleMoleculeMagneticTorqueTweezerRequest(BaseModel):
    name: str = Field(..., example="Autonomous Single-Molecule Magnetic Torque Tweezers (MTT) DNA Supercoiling & Twist Modeler Run")
    target_specimen: str = Field(default="Tethered 10-kb Double-Stranded DNA Molecule with Cylindrical Magnetic Bead in Horizontal Torque Field")
    analytical_modality: str = Field(default="magnetic-torque-tweezers-supercoiling")
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


class SingleMoleculeMagneticTorqueTweezerStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    torsional_persistence_length_nm: float
    buckling_transition_critical_torque_pN_nm: float
    plectoneme_supercoil_conformation_density: float
    dna_twist_stretch_coupling_constant_pN: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=SingleMoleculeMagneticTorqueTweezerStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_single_molecule_magnetic_torque_tweezer(
    req: AnalyzeSingleMoleculeMagneticTorqueTweezerRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Single-Molecule Magnetic Torque Tweezers (MTT) DNA Supercoiling & Twist Modeler analysis and persist study."""
    engine = SingleMoleculeMagneticTorqueTweezerEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SingleMoleculeMagneticTorqueTweezerRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        torsional_persistence_length_nm=result.torsional_persistence_length_nm,
        buckling_transition_critical_torque_pN_nm=result.buckling_transition_critical_torque_pN_nm,
        plectoneme_supercoil_conformation_density=result.plectoneme_supercoil_conformation_density,
        dna_twist_stretch_coupling_constant_pN=result.dna_twist_stretch_coupling_constant_pN,
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

    return SingleMoleculeMagneticTorqueTweezerStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        torsional_persistence_length_nm=study.torsional_persistence_length_nm,
        buckling_transition_critical_torque_pN_nm=study.buckling_transition_critical_torque_pN_nm,
        plectoneme_supercoil_conformation_density=study.plectoneme_supercoil_conformation_density,
        dna_twist_stretch_coupling_constant_pN=study.dna_twist_stretch_coupling_constant_pN,
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


@router.get("/studies", response_model=List[SingleMoleculeMagneticTorqueTweezerStudyResponse])
async def list_single_molecule_magnetic_torque_tweezer_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Single-Molecule Magnetic Torque Tweezers (MTT) DNA Supercoiling & Twist Modeler studies."""
    repo = SingleMoleculeMagneticTorqueTweezerRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SingleMoleculeMagneticTorqueTweezerStudyResponse)
async def get_single_molecule_magnetic_torque_tweezer_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Single-Molecule Magnetic Torque Tweezers (MTT) DNA Supercoiling & Twist Modeler study by ID."""
    repo = SingleMoleculeMagneticTorqueTweezerRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
