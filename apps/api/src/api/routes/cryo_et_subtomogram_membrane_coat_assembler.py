"""FastAPI route for Phase 575: Autonomous In-Situ Cryo-ET Subtomogram Averaging Clathrin & COP-II Vesicular Membrane Coat Symmetry Assembler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.cryo_et_subtomogram_membrane_coat_assembler_repo import CryoEtSubtomogramMembraneCoatAssemblerRepository
from research.orchestration.cryo_et_subtomogram_membrane_coat_assembler_engine import CryoEtSubtomogramMembraneCoatAssemblerEngine

router = APIRouter(prefix="/cryo-et-subtomogram-membrane-coat-assembler", tags=["Phase 575 - Autonomous In-Situ Cryo-ET Subtomogram Averaging Clathrin & COP-II Vesicular Membrane Coat Symmetry Assembler"])


class CryoEtSubtomogramMembraneCoatAssemblerAnalyzeRequest(BaseModel):
    name: str = Field(default="Autonomous In-Situ Cryo-ET Subtomogram Averaging Clathrin & COP-II Vesicular Membrane Coat Symmetry Assembler Study")
    target_specimen: Optional[str] = Field(default="Vitrified Saccharomyces cerevisiae Budding Vesicle Donor Sites with COP-II Polyhedral Lattice Outer Shell")
    analytical_modality: Optional[str] = Field(default="cryoet-subtomogram-coat-assembly")
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


class CryoEtSubtomogramMembraneCoatAssemblerStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    subtomogram_resolution_fsc0143_a: float
    cage_polyhedral_symmetry_index: float
    membrane_curvature_coupling_energy_kbt: float
    angular_orientation_precision_deg: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []


@router.post("/analyze", response_model=CryoEtSubtomogramMembraneCoatAssemblerStudyResponse)
async def analyze_cryo_et_subtomogram_membrane_coat_assembler(
    req: CryoEtSubtomogramMembraneCoatAssemblerAnalyzeRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Execute autonomous analysis for Autonomous In-Situ Cryo-ET Subtomogram Averaging Clathrin & COP-II Vesicular Membrane Coat Symmetry Assembler."""
    engine = CryoEtSubtomogramMembraneCoatAssemblerEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = CryoEtSubtomogramMembraneCoatAssemblerRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        subtomogram_resolution_fsc0143_a=result.subtomogram_resolution_fsc0143_a,
        cage_polyhedral_symmetry_index=result.cage_polyhedral_symmetry_index,
        membrane_curvature_coupling_energy_kbt=result.membrane_curvature_coupling_energy_kbt,
        angular_orientation_precision_deg=result.angular_orientation_precision_deg,
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

    return CryoEtSubtomogramMembraneCoatAssemblerStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        subtomogram_resolution_fsc0143_a=study.subtomogram_resolution_fsc0143_a,
        cage_polyhedral_symmetry_index=study.cage_polyhedral_symmetry_index,
        membrane_curvature_coupling_energy_kbt=study.membrane_curvature_coupling_energy_kbt,
        angular_orientation_precision_deg=study.angular_orientation_precision_deg,
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


@router.get("/studies", response_model=List[CryoEtSubtomogramMembraneCoatAssemblerStudyResponse])
async def list_cryo_et_subtomogram_membrane_coat_assembler_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous In-Situ Cryo-ET Subtomogram Averaging Clathrin & COP-II Vesicular Membrane Coat Symmetry Assembler studies."""
    repo = CryoEtSubtomogramMembraneCoatAssemblerRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=CryoEtSubtomogramMembraneCoatAssemblerStudyResponse)
async def get_cryo_et_subtomogram_membrane_coat_assembler_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous In-Situ Cryo-ET Subtomogram Averaging Clathrin & COP-II Vesicular Membrane Coat Symmetry Assembler study by ID."""
    repo = CryoEtSubtomogramMembraneCoatAssemblerRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
