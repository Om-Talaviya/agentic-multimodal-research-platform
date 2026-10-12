"""FastAPI routes for Phase 436: Autonomous Diamond NV-Center Nanoscale Single-Molecule Magnetic Resonance Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.single_molecule_magnetic_resonance_nv_center_repo import SingleMoleculeNvCenterNmrRepository
from research.orchestration.single_molecule_magnetic_resonance_nv_center_engine import SingleMoleculeNvCenterNmrEngine

router = APIRouter(prefix="/single-molecule-nv-center-nmr", tags=["single-molecule-nv-center-nmr"])


class AnalyzeSingleMoleculeNvCenterNmrRequest(BaseModel):
    name: str = Field(..., example="Autonomous Diamond NV-Center Nanoscale Single-Molecule Magnetic Resonance Engine Run")
    target_specimen: str = Field(default="Diamond Nitrogen-Vacancy (NV) Center Nanocrystal with Surface Immobilized Ferritin")
    analytical_modality: str = Field(default="nv-center-nanoscale-nmr")
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


class SingleMoleculeNvCenterNmrStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    spin_coherence_time_t2_us: float
    magnetic_sensitivity_nT_per_sqrthz: float
    optically_detected_mr_dip_contrast: float
    spatial_standoff_distance_nm: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=SingleMoleculeNvCenterNmrStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_single_molecule_magnetic_resonance_nv_center(
    req: AnalyzeSingleMoleculeNvCenterNmrRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Diamond NV-Center Nanoscale Single-Molecule Magnetic Resonance Engine analysis and persist study."""
    engine = SingleMoleculeNvCenterNmrEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SingleMoleculeNvCenterNmrRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        spin_coherence_time_t2_us=result.spin_coherence_time_t2_us,
        magnetic_sensitivity_nT_per_sqrthz=result.magnetic_sensitivity_nT_per_sqrthz,
        optically_detected_mr_dip_contrast=result.optically_detected_mr_dip_contrast,
        spatial_standoff_distance_nm=result.spatial_standoff_distance_nm,
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

    return SingleMoleculeNvCenterNmrStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        spin_coherence_time_t2_us=study.spin_coherence_time_t2_us,
        magnetic_sensitivity_nT_per_sqrthz=study.magnetic_sensitivity_nT_per_sqrthz,
        optically_detected_mr_dip_contrast=study.optically_detected_mr_dip_contrast,
        spatial_standoff_distance_nm=study.spatial_standoff_distance_nm,
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


@router.get("/studies", response_model=List[SingleMoleculeNvCenterNmrStudyResponse])
async def list_single_molecule_magnetic_resonance_nv_center_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Diamond NV-Center Nanoscale Single-Molecule Magnetic Resonance Engine studies."""
    repo = SingleMoleculeNvCenterNmrRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SingleMoleculeNvCenterNmrStudyResponse)
async def get_single_molecule_magnetic_resonance_nv_center_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Diamond NV-Center Nanoscale Single-Molecule Magnetic Resonance Engine study by ID."""
    repo = SingleMoleculeNvCenterNmrRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
