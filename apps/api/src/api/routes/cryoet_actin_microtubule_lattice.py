"""FastAPI routes for Phase 469: Autonomous In-Situ Cryo-ET Cytoskeletal Actin-Microtubule Cross-Linking Structural Lattice Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.cryoet_actin_microtubule_lattice_repo import CryoetActinMicrotubuleLatticeRepository
from research.orchestration.cryoet_actin_microtubule_lattice_engine import CryoetActinMicrotubuleLatticeEngine

router = APIRouter(prefix="/cryoet-actin-microtubule-lattice", tags=["cryoet-actin-microtubule-lattice"])


class AnalyzeCryoetActinMicrotubuleLatticeRequest(BaseModel):
    name: str = Field(..., example="Autonomous In-Situ Cryo-ET Cytoskeletal Actin-Microtubule Cross-Linking Structural Lattice Engine Run")
    target_specimen: str = Field(default="Vitrified Primary Growth Cone Cytoskeleton with Septin/Plectin Cross-Linked Filament Assemblies")
    analytical_modality: str = Field(default="cryoet-actin-microtubule-lattice")
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


class CryoetActinMicrotubuleLatticeStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    crosslinker_bridge_density_per_um: float
    filament_intersection_angle_distribution_deg: float
    subtomogram_correlation_resolution_angstrom: float
    cytoskeletal_network_rigidity_percolation_tau: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=CryoetActinMicrotubuleLatticeStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_cryoet_actin_microtubule_lattice(
    req: AnalyzeCryoetActinMicrotubuleLatticeRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous In-Situ Cryo-ET Cytoskeletal Actin-Microtubule Cross-Linking Structural Lattice Engine analysis and persist study."""
    engine = CryoetActinMicrotubuleLatticeEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = CryoetActinMicrotubuleLatticeRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        crosslinker_bridge_density_per_um=result.crosslinker_bridge_density_per_um,
        filament_intersection_angle_distribution_deg=result.filament_intersection_angle_distribution_deg,
        subtomogram_correlation_resolution_angstrom=result.subtomogram_correlation_resolution_angstrom,
        cytoskeletal_network_rigidity_percolation_tau=result.cytoskeletal_network_rigidity_percolation_tau,
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

    return CryoetActinMicrotubuleLatticeStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        crosslinker_bridge_density_per_um=study.crosslinker_bridge_density_per_um,
        filament_intersection_angle_distribution_deg=study.filament_intersection_angle_distribution_deg,
        subtomogram_correlation_resolution_angstrom=study.subtomogram_correlation_resolution_angstrom,
        cytoskeletal_network_rigidity_percolation_tau=study.cytoskeletal_network_rigidity_percolation_tau,
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


@router.get("/studies", response_model=List[CryoetActinMicrotubuleLatticeStudyResponse])
async def list_cryoet_actin_microtubule_lattice_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous In-Situ Cryo-ET Cytoskeletal Actin-Microtubule Cross-Linking Structural Lattice Engine studies."""
    repo = CryoetActinMicrotubuleLatticeRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=CryoetActinMicrotubuleLatticeStudyResponse)
async def get_cryoet_actin_microtubule_lattice_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous In-Situ Cryo-ET Cytoskeletal Actin-Microtubule Cross-Linking Structural Lattice Engine study by ID."""
    repo = CryoetActinMicrotubuleLatticeRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
