"""FastAPI routes for Phase 495: Autonomous Spatial Multi-Modal Epigenomic CUT&Tag-RNA Joint Profiling Diffusion Trajectory Mapper."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.cuttag_rna_joint_diffusion_trajectory_repo import CuttagRnaJointDiffusionTrajectoryRepository
from research.orchestration.cuttag_rna_joint_diffusion_trajectory_engine import CuttagRnaJointDiffusionTrajectoryEngine

router = APIRouter(prefix="/cuttag-rna-joint-diffusion-trajectory", tags=["cuttag-rna-joint-diffusion-trajectory"])


class AnalyzeCuttagRnaJointDiffusionTrajectoryRequest(BaseModel):
    name: str = Field(..., example="Autonomous Spatial Multi-Modal Epigenomic CUT&Tag-RNA Joint Profiling Diffusion Trajectory Mapper Run")
    target_specimen: str = Field(default="Developing Murine Cortical Plate Radial Glia Lineage with H3K4me3 / H3K27ac and mRNA Co-Assay")
    analytical_modality: str = Field(default="cuttag-rna-joint-diffusion")
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


class CuttagRnaJointDiffusionTrajectoryStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    epigenomic_chromatin_velocity_coherence: float
    promoter_enhancer_concordance_score: float
    diffusion_pseudotime_lineage_resolution_tau: float
    joint_latent_space_neighbor_overlap_pct: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=CuttagRnaJointDiffusionTrajectoryStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_cuttag_rna_joint_diffusion_trajectory(
    req: AnalyzeCuttagRnaJointDiffusionTrajectoryRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Spatial Multi-Modal Epigenomic CUT&Tag-RNA Joint Profiling Diffusion Trajectory Mapper analysis and persist study."""
    engine = CuttagRnaJointDiffusionTrajectoryEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = CuttagRnaJointDiffusionTrajectoryRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        epigenomic_chromatin_velocity_coherence=result.epigenomic_chromatin_velocity_coherence,
        promoter_enhancer_concordance_score=result.promoter_enhancer_concordance_score,
        diffusion_pseudotime_lineage_resolution_tau=result.diffusion_pseudotime_lineage_resolution_tau,
        joint_latent_space_neighbor_overlap_pct=result.joint_latent_space_neighbor_overlap_pct,
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

    return CuttagRnaJointDiffusionTrajectoryStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        epigenomic_chromatin_velocity_coherence=study.epigenomic_chromatin_velocity_coherence,
        promoter_enhancer_concordance_score=study.promoter_enhancer_concordance_score,
        diffusion_pseudotime_lineage_resolution_tau=study.diffusion_pseudotime_lineage_resolution_tau,
        joint_latent_space_neighbor_overlap_pct=study.joint_latent_space_neighbor_overlap_pct,
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


@router.get("/studies", response_model=List[CuttagRnaJointDiffusionTrajectoryStudyResponse])
async def list_cuttag_rna_joint_diffusion_trajectory_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Spatial Multi-Modal Epigenomic CUT&Tag-RNA Joint Profiling Diffusion Trajectory Mapper studies."""
    repo = CuttagRnaJointDiffusionTrajectoryRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=CuttagRnaJointDiffusionTrajectoryStudyResponse)
async def get_cuttag_rna_joint_diffusion_trajectory_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Spatial Multi-Modal Epigenomic CUT&Tag-RNA Joint Profiling Diffusion Trajectory Mapper study by ID."""
    repo = CuttagRnaJointDiffusionTrajectoryRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
