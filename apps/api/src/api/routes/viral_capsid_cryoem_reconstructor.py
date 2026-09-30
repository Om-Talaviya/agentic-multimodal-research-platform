"""FastAPI routes for Phase 398: High-Resolution Icosahedral Viral Capsid Cryo-EM Symmetry Reconstructor Studio."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.viral_capsid_cryoem_reconstructor_repo import ViralCapsidCryoemReconstructorRepository
from research.orchestration.viral_capsid_cryoem_reconstructor_engine import ViralCapsidCryoemReconstructorEngine

router = APIRouter(prefix="/viral-capsid-cryoem-reconstructor", tags=["viral-capsid-cryoem-reconstructor"])


class AnalyzeViralCapsidCryoemReconstructorRequest(BaseModel):
    name: str = Field(..., example="Autonomous High-Resolution Icosahedral Viral Capsid Cryo-EM Symmetry Reconstructor Run")
    target_specimen: str = Field(default="Human Patient Cohort Sample")
    analytical_modality: str = Field(default="viral-capsid-cryoem-reconstruction")
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


class ViralCapsidCryoemReconstructorStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    reconstructed_cryo_em_map_fsc_resolution_angstrom: float
    icosahedral_symmetry_alignment_angular_precision_deg: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=ViralCapsidCryoemReconstructorStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_viral_capsid_cryoem_reconstructor(
    req: AnalyzeViralCapsidCryoemReconstructorRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous High-Resolution Icosahedral Viral Capsid Cryo-EM Symmetry Reconstructor analysis and persist study record."""
    engine = ViralCapsidCryoemReconstructorEngine()
    analysis = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = ViralCapsidCryoemReconstructorRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=analysis.target_specimen,
        analytical_modality=analysis.analytical_modality,
        reconstructed_cryo_em_map_fsc_resolution_angstrom=getattr(analysis, "reconstructed_cryo_em_map_fsc_resolution_angstrom"),
        icosahedral_symmetry_alignment_angular_precision_deg=getattr(analysis, "icosahedral_symmetry_alignment_angular_precision_deg"),
        confidence_score=analysis.confidence_score,
        status="completed",
        summary_report=analysis.summary_report,
    )

    for it in analysis.item_profiles:
        await repo.add_item_profile(
            study_id=study.id,
            item_name=it.item_name,
            profile_category=it.profile_category,
            quantitative_value=it.quantitative_value,
            log2_fold_change=it.log2_fold_change,
            significance_score=it.significance_score,
        )

    for tr in analysis.metric_traces:
        await repo.add_metric_trace(
            study_id=study.id,
            metric_dimension=tr.metric_dimension,
            observed_value=tr.observed_value,
            z_score=tr.z_score,
            p_value=tr.p_value,
        )

    return ViralCapsidCryoemReconstructorStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        reconstructed_cryo_em_map_fsc_resolution_angstrom=getattr(study, "reconstructed_cryo_em_map_fsc_resolution_angstrom"),
        icosahedral_symmetry_alignment_angular_precision_deg=getattr(study, "icosahedral_symmetry_alignment_angular_precision_deg"),
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
            ) for it in analysis.item_profiles
        ],
        metric_traces=[
            MetricTraceResponse(
                metric_dimension=tr.metric_dimension,
                observed_value=tr.observed_value,
                z_score=tr.z_score,
                p_value=tr.p_value,
            ) for tr in analysis.metric_traces
        ],
    )


@router.get("/studies", response_model=List[ViralCapsidCryoemReconstructorStudyResponse])
async def list_viral_capsid_cryoem_reconstructor_studies(
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List historical High-Resolution Icosahedral Viral Capsid Cryo-EM Symmetry Reconstructor studies."""
    repo = ViralCapsidCryoemReconstructorRepository(session)
    studies = await repo.list_studies(limit=limit)
    return [
        ViralCapsidCryoemReconstructorStudyResponse(
            id=s.id,
            name=s.name,
            target_specimen=s.target_specimen,
            analytical_modality=s.analytical_modality,
            reconstructed_cryo_em_map_fsc_resolution_angstrom=getattr(s, "reconstructed_cryo_em_map_fsc_resolution_angstrom"),
            icosahedral_symmetry_alignment_angular_precision_deg=getattr(s, "icosahedral_symmetry_alignment_angular_precision_deg"),
            confidence_score=s.confidence_score,
            status=s.status,
            summary_report=s.summary_report,
            item_profiles=[],
            metric_traces=[],
        ) for s in studies
    ]


@router.get("/studies/{study_id}", response_model=ViralCapsidCryoemReconstructorStudyResponse)
async def get_viral_capsid_cryoem_reconstructor_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve details for a single High-Resolution Icosahedral Viral Capsid Cryo-EM Symmetry Reconstructor study."""
    repo = ViralCapsidCryoemReconstructorRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Study not found")
    return ViralCapsidCryoemReconstructorStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        reconstructed_cryo_em_map_fsc_resolution_angstrom=getattr(study, "reconstructed_cryo_em_map_fsc_resolution_angstrom"),
        icosahedral_symmetry_alignment_angular_precision_deg=getattr(study, "icosahedral_symmetry_alignment_angular_precision_deg"),
        confidence_score=study.confidence_score,
        status=study.status,
        summary_report=study.summary_report,
        item_profiles=[],
        metric_traces=[],
    )
