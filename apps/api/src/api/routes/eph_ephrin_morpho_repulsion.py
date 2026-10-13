"""FastAPI routes for Phase 468: Autonomous Synthetic Morphogenetic Morpho-Kinetic Boundary Sharpening & Eph-Ephrin Repulsion Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.eph_ephrin_morpho_repulsion_repo import EphEphrinMorphoRepulsionRepository
from research.orchestration.eph_ephrin_morpho_repulsion_engine import EphEphrinMorphoRepulsionEngine

router = APIRouter(prefix="/eph-ephrin-morpho-repulsion", tags=["eph-ephrin-morpho-repulsion"])


class AnalyzeEphEphrinMorphoRepulsionRequest(BaseModel):
    name: str = Field(..., example="Autonomous Synthetic Morphogenetic Morpho-Kinetic Boundary Sharpening & Eph-Ephrin Repulsion Engine Run")
    target_specimen: str = Field(default="HEK293T EphB2/EphrinB1 Co-Culture Mosaic Boundary Array in Micropatterned Substrates")
    analytical_modality: str = Field(default="eph-ephrin-morpho-repulsion")
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


class EphEphrinMorphoRepulsionStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    interface_roughness_boundary_width_um: float
    eph_receptor_clustering_density_per_um2: float
    contact_repulsion_retraction_velocity_um_min: float
    heterotypic_sorting_order_parameter: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=EphEphrinMorphoRepulsionStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_eph_ephrin_morpho_repulsion(
    req: AnalyzeEphEphrinMorphoRepulsionRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Synthetic Morphogenetic Morpho-Kinetic Boundary Sharpening & Eph-Ephrin Repulsion Engine analysis and persist study."""
    engine = EphEphrinMorphoRepulsionEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = EphEphrinMorphoRepulsionRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        interface_roughness_boundary_width_um=result.interface_roughness_boundary_width_um,
        eph_receptor_clustering_density_per_um2=result.eph_receptor_clustering_density_per_um2,
        contact_repulsion_retraction_velocity_um_min=result.contact_repulsion_retraction_velocity_um_min,
        heterotypic_sorting_order_parameter=result.heterotypic_sorting_order_parameter,
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

    return EphEphrinMorphoRepulsionStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        interface_roughness_boundary_width_um=study.interface_roughness_boundary_width_um,
        eph_receptor_clustering_density_per_um2=study.eph_receptor_clustering_density_per_um2,
        contact_repulsion_retraction_velocity_um_min=study.contact_repulsion_retraction_velocity_um_min,
        heterotypic_sorting_order_parameter=study.heterotypic_sorting_order_parameter,
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


@router.get("/studies", response_model=List[EphEphrinMorphoRepulsionStudyResponse])
async def list_eph_ephrin_morpho_repulsion_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Synthetic Morphogenetic Morpho-Kinetic Boundary Sharpening & Eph-Ephrin Repulsion Engine studies."""
    repo = EphEphrinMorphoRepulsionRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=EphEphrinMorphoRepulsionStudyResponse)
async def get_eph_ephrin_morpho_repulsion_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Synthetic Morphogenetic Morpho-Kinetic Boundary Sharpening & Eph-Ephrin Repulsion Engine study by ID."""
    repo = EphEphrinMorphoRepulsionRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
