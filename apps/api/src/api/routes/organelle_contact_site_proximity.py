"""FastAPI routes for Phase 429: Autonomous Whole-Cell Organelle Contact Site & Membrane Proximity Distance Transformer."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.organelle_contact_site_proximity_repo import OrganelleContactSiteProximityRepository
from research.orchestration.organelle_contact_site_proximity_engine import OrganelleContactSiteProximityEngine

router = APIRouter(prefix="/organelle-contact-site-proximity", tags=["organelle-contact-site-proximity"])


class AnalyzeOrganelleContactSiteProximityRequest(BaseModel):
    name: str = Field(..., example="Autonomous Whole-Cell Organelle Contact Site & Membrane Proximity Distance Transformer Run")
    target_specimen: str = Field(default="Focused Ion Beam Scanning Electron Microscopy (FIB-SEM) Whole Cell")
    analytical_modality: str = Field(default="organelle-contact-site")
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


class OrganelleContactSiteProximityStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    er_mitochondria_contact_distance_nm: float
    contact_site_surface_area_um2: float
    lipid_transfer_flux_rate: float
    organelle_tethering_density: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=OrganelleContactSiteProximityStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_organelle_contact_site_proximity(
    req: AnalyzeOrganelleContactSiteProximityRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Whole-Cell Organelle Contact Site & Membrane Proximity Distance Transformer analysis and persist study."""
    engine = OrganelleContactSiteProximityEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = OrganelleContactSiteProximityRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        er_mitochondria_contact_distance_nm=result.er_mitochondria_contact_distance_nm,
        contact_site_surface_area_um2=result.contact_site_surface_area_um2,
        lipid_transfer_flux_rate=result.lipid_transfer_flux_rate,
        organelle_tethering_density=result.organelle_tethering_density,
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

    return OrganelleContactSiteProximityStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        er_mitochondria_contact_distance_nm=study.er_mitochondria_contact_distance_nm,
        contact_site_surface_area_um2=study.contact_site_surface_area_um2,
        lipid_transfer_flux_rate=study.lipid_transfer_flux_rate,
        organelle_tethering_density=study.organelle_tethering_density,
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


@router.get("/studies", response_model=List[OrganelleContactSiteProximityStudyResponse])
async def list_organelle_contact_site_proximity_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Whole-Cell Organelle Contact Site & Membrane Proximity Distance Transformer studies."""
    repo = OrganelleContactSiteProximityRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=OrganelleContactSiteProximityStudyResponse)
async def get_organelle_contact_site_proximity_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Whole-Cell Organelle Contact Site & Membrane Proximity Distance Transformer study by ID."""
    repo = OrganelleContactSiteProximityRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
