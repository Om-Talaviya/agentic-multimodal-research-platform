"""FastAPI routes for Phase 481: Autonomous In-Situ Cryo-ET Ribosome Polysome Structural Topology & Nascent Chain Chaperone Coordinator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.cryoet_polysome_chaperone_topology_repo import CryoetPolysomeChaperoneTopologyRepository
from research.orchestration.cryoet_polysome_chaperone_topology_engine import CryoetPolysomeChaperoneTopologyEngine

router = APIRouter(prefix="/cryoet-polysome-chaperone-topology", tags=["cryoet-polysome-chaperone-topology"])


class AnalyzeCryoetPolysomeChaperoneTopologyRequest(BaseModel):
    name: str = Field(..., example="Autonomous In-Situ Cryo-ET Ribosome Polysome Structural Topology & Nascent Chain Chaperone Coordinator Run")
    target_specimen: str = Field(default="Vitrified Mammalian Reticulocyte Cytoplasm with Circular Polysome-Hsp70 Chaperone Ensembles")
    analytical_modality: str = Field(default="cryoet-polysome-topology")
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


class CryoetPolysomeChaperoneTopologyStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    inter_ribosomal_exit_channel_distance_nm: float
    polysome_circularity_topology_index: float
    chaperone_nascent_chain_occupancy_ratio: float
    subtomogram_averaging_resolution_angstrom: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=CryoetPolysomeChaperoneTopologyStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_cryoet_polysome_chaperone_topology(
    req: AnalyzeCryoetPolysomeChaperoneTopologyRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous In-Situ Cryo-ET Ribosome Polysome Structural Topology & Nascent Chain Chaperone Coordinator analysis and persist study."""
    engine = CryoetPolysomeChaperoneTopologyEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = CryoetPolysomeChaperoneTopologyRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        inter_ribosomal_exit_channel_distance_nm=result.inter_ribosomal_exit_channel_distance_nm,
        polysome_circularity_topology_index=result.polysome_circularity_topology_index,
        chaperone_nascent_chain_occupancy_ratio=result.chaperone_nascent_chain_occupancy_ratio,
        subtomogram_averaging_resolution_angstrom=result.subtomogram_averaging_resolution_angstrom,
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

    return CryoetPolysomeChaperoneTopologyStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        inter_ribosomal_exit_channel_distance_nm=study.inter_ribosomal_exit_channel_distance_nm,
        polysome_circularity_topology_index=study.polysome_circularity_topology_index,
        chaperone_nascent_chain_occupancy_ratio=study.chaperone_nascent_chain_occupancy_ratio,
        subtomogram_averaging_resolution_angstrom=study.subtomogram_averaging_resolution_angstrom,
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


@router.get("/studies", response_model=List[CryoetPolysomeChaperoneTopologyStudyResponse])
async def list_cryoet_polysome_chaperone_topology_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous In-Situ Cryo-ET Ribosome Polysome Structural Topology & Nascent Chain Chaperone Coordinator studies."""
    repo = CryoetPolysomeChaperoneTopologyRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=CryoetPolysomeChaperoneTopologyStudyResponse)
async def get_cryoet_polysome_chaperone_topology_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous In-Situ Cryo-ET Ribosome Polysome Structural Topology & Nascent Chain Chaperone Coordinator study by ID."""
    repo = CryoetPolysomeChaperoneTopologyRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
