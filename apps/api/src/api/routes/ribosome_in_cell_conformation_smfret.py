"""FastAPI routes for Phase 505: Autonomous In-Cell Single-Molecule FRET Ribosome Conformational Dynamics Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.ribosome_in_cell_conformation_smfret_repo import RibosomeInCellConformationSmfretRepository
from research.orchestration.ribosome_in_cell_conformation_smfret_engine import RibosomeInCellConformationSmfretEngine

router = APIRouter(prefix="/ribosome-in-cell-conformation-smfret", tags=["ribosome-in-cell-conformation-smfret"])


class AnalyzeRibosomeInCellConformationSmfretRequest(BaseModel):
    name: str = Field(..., example="Autonomous In-Cell Single-Molecule FRET Ribosome Conformational Dynamics Engine Run")
    target_specimen: str = Field(default="Intact Vitrified E. coli Cell with Dual-Fluorophore Cy3/Cy5 L11-Stalk Ribosomal Probes")
    analytical_modality: str = Field(default="in-cell-smfret-ribosome")
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


class RibosomeInCellConformationSmfretStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    intersubunit_rotation_fret_efficiency: float
    translation_elongation_cycle_rate_s_inv: float
    crowding_induced_stalk_fluctuation_std: float
    intact_cell_fluorophore_photobleaching_lifetime_s: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=RibosomeInCellConformationSmfretStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_ribosome_in_cell_conformation_smfret(
    req: AnalyzeRibosomeInCellConformationSmfretRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous In-Cell Single-Molecule FRET Ribosome Conformational Dynamics Engine analysis and persist study."""
    engine = RibosomeInCellConformationSmfretEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = RibosomeInCellConformationSmfretRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        intersubunit_rotation_fret_efficiency=result.intersubunit_rotation_fret_efficiency,
        translation_elongation_cycle_rate_s_inv=result.translation_elongation_cycle_rate_s_inv,
        crowding_induced_stalk_fluctuation_std=result.crowding_induced_stalk_fluctuation_std,
        intact_cell_fluorophore_photobleaching_lifetime_s=result.intact_cell_fluorophore_photobleaching_lifetime_s,
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

    return RibosomeInCellConformationSmfretStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        intersubunit_rotation_fret_efficiency=study.intersubunit_rotation_fret_efficiency,
        translation_elongation_cycle_rate_s_inv=study.translation_elongation_cycle_rate_s_inv,
        crowding_induced_stalk_fluctuation_std=study.crowding_induced_stalk_fluctuation_std,
        intact_cell_fluorophore_photobleaching_lifetime_s=study.intact_cell_fluorophore_photobleaching_lifetime_s,
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


@router.get("/studies", response_model=List[RibosomeInCellConformationSmfretStudyResponse])
async def list_ribosome_in_cell_conformation_smfret_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous In-Cell Single-Molecule FRET Ribosome Conformational Dynamics Engine studies."""
    repo = RibosomeInCellConformationSmfretRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=RibosomeInCellConformationSmfretStudyResponse)
async def get_ribosome_in_cell_conformation_smfret_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous In-Cell Single-Molecule FRET Ribosome Conformational Dynamics Engine study by ID."""
    repo = RibosomeInCellConformationSmfretRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
