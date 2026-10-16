"""FastAPI route for Phase 573: Autonomous Equivariant SE(3) Diffusion Deep Learning Protein-Protein Interaction (PPI) Complex Docking & Binding Affinity Forecaster."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.deep_learning_protein_protein_docking_affinity_repo import DeepLearningProteinProteinDockingAffinityRepository
from research.orchestration.deep_learning_protein_protein_docking_affinity_engine import DeepLearningProteinProteinDockingAffinityEngine

router = APIRouter(prefix="/deep-learning-protein-protein-docking-affinity", tags=["Phase 573 - Autonomous Equivariant SE(3) Diffusion Deep Learning Protein-Protein Interaction (PPI) Complex Docking & Binding Affinity Forecaster"])


class DeepLearningProteinProteinDockingAffinityAnalyzeRequest(BaseModel):
    name: str = Field(default="Autonomous Equivariant SE(3) Diffusion Deep Learning Protein-Protein Interaction (PPI) Complex Docking & Binding Affinity Forecaster Study")
    target_specimen: Optional[str] = Field(default="SARS-CoV-2 Spike Receptor-Binding Domain Complexed with Engineered Nanobody Nb21-Fc Variant")
    analytical_modality: Optional[str] = Field(default="se3-diffusion-ppi-docking")
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


class DeepLearningProteinProteinDockingAffinityStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    interface_rmsd_angstrom: float
    binding_free_energy_delta_g_kcal_mol: float
    docking_pose_confidence_plddt: float
    buried_surface_area_angstrom2: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []


@router.post("/analyze", response_model=DeepLearningProteinProteinDockingAffinityStudyResponse)
async def analyze_deep_learning_protein_protein_docking_affinity(
    req: DeepLearningProteinProteinDockingAffinityAnalyzeRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Execute autonomous analysis for Autonomous Equivariant SE(3) Diffusion Deep Learning Protein-Protein Interaction (PPI) Complex Docking & Binding Affinity Forecaster."""
    engine = DeepLearningProteinProteinDockingAffinityEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = DeepLearningProteinProteinDockingAffinityRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        interface_rmsd_angstrom=result.interface_rmsd_angstrom,
        binding_free_energy_delta_g_kcal_mol=result.binding_free_energy_delta_g_kcal_mol,
        docking_pose_confidence_plddt=result.docking_pose_confidence_plddt,
        buried_surface_area_angstrom2=result.buried_surface_area_angstrom2,
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

    return DeepLearningProteinProteinDockingAffinityStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        interface_rmsd_angstrom=study.interface_rmsd_angstrom,
        binding_free_energy_delta_g_kcal_mol=study.binding_free_energy_delta_g_kcal_mol,
        docking_pose_confidence_plddt=study.docking_pose_confidence_plddt,
        buried_surface_area_angstrom2=study.buried_surface_area_angstrom2,
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


@router.get("/studies", response_model=List[DeepLearningProteinProteinDockingAffinityStudyResponse])
async def list_deep_learning_protein_protein_docking_affinity_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Equivariant SE(3) Diffusion Deep Learning Protein-Protein Interaction (PPI) Complex Docking & Binding Affinity Forecaster studies."""
    repo = DeepLearningProteinProteinDockingAffinityRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=DeepLearningProteinProteinDockingAffinityStudyResponse)
async def get_deep_learning_protein_protein_docking_affinity_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Equivariant SE(3) Diffusion Deep Learning Protein-Protein Interaction (PPI) Complex Docking & Binding Affinity Forecaster study by ID."""
    repo = DeepLearningProteinProteinDockingAffinityRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
