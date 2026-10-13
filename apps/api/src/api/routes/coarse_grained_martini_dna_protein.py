"""FastAPI routes for Phase 447: Autonomous Coarse-Grained DNA-Protein Complex Martini Force-Field Molecular Dynamics Simulator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.coarse_grained_martini_dna_protein_repo import CoarseGrainedMartiniDnaProteinRepository
from research.orchestration.coarse_grained_martini_dna_protein_engine import CoarseGrainedMartiniDnaProteinEngine

router = APIRouter(prefix="/coarse-grained-martini-dynamics", tags=["coarse-grained-martini-dynamics"])


class AnalyzeCoarseGrainedMartiniDnaProteinRequest(BaseModel):
    name: str = Field(..., example="Autonomous Coarse-Grained DNA-Protein Complex Martini Force-Field Molecular Dynamics Simulator Run")
    target_specimen: str = Field(default="Nucleosome Core Particle Octamer with 147bp Wrapped DNA in 150mM Salt Solvation Box")
    analytical_modality: str = Field(default="coarse-grained-martini-dynamics")
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


class CoarseGrainedMartiniDnaProteinStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    bead_rmsd_convergence_angstrom: float
    electrostatic_solvation_free_energy_kcal_mol: float
    conformational_sampling_speedup_factor: float
    contact_pair_distribution_g_r: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=CoarseGrainedMartiniDnaProteinStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_coarse_grained_martini_dna_protein(
    req: AnalyzeCoarseGrainedMartiniDnaProteinRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Coarse-Grained DNA-Protein Complex Martini Force-Field Molecular Dynamics Simulator analysis and persist study."""
    engine = CoarseGrainedMartiniDnaProteinEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = CoarseGrainedMartiniDnaProteinRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        bead_rmsd_convergence_angstrom=result.bead_rmsd_convergence_angstrom,
        electrostatic_solvation_free_energy_kcal_mol=result.electrostatic_solvation_free_energy_kcal_mol,
        conformational_sampling_speedup_factor=result.conformational_sampling_speedup_factor,
        contact_pair_distribution_g_r=result.contact_pair_distribution_g_r,
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

    return CoarseGrainedMartiniDnaProteinStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        bead_rmsd_convergence_angstrom=study.bead_rmsd_convergence_angstrom,
        electrostatic_solvation_free_energy_kcal_mol=study.electrostatic_solvation_free_energy_kcal_mol,
        conformational_sampling_speedup_factor=study.conformational_sampling_speedup_factor,
        contact_pair_distribution_g_r=study.contact_pair_distribution_g_r,
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


@router.get("/studies", response_model=List[CoarseGrainedMartiniDnaProteinStudyResponse])
async def list_coarse_grained_martini_dna_protein_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Coarse-Grained DNA-Protein Complex Martini Force-Field Molecular Dynamics Simulator studies."""
    repo = CoarseGrainedMartiniDnaProteinRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=CoarseGrainedMartiniDnaProteinStudyResponse)
async def get_coarse_grained_martini_dna_protein_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Coarse-Grained DNA-Protein Complex Martini Force-Field Molecular Dynamics Simulator study by ID."""
    repo = CoarseGrainedMartiniDnaProteinRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
