"""FastAPI routes for Phase 541: Autonomous Synthetic Protocellular Compartment FtsZ-Min System Dynamic Cleavage Constriction Modeler."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.synthetic_cell_division_ftsz_constriction_repo import SyntheticCellDivisionFtszConstrictionRepository
from research.orchestration.synthetic_cell_division_ftsz_constriction_engine import SyntheticCellDivisionFtszConstrictionEngine

router = APIRouter(prefix="/synthetic-cell-division-ftsz-constriction", tags=["synthetic-cell-division-ftsz-constriction"])


class AnalyzeSyntheticCellDivisionFtszConstrictionRequest(BaseModel):
    name: str = Field(..., example="Autonomous Synthetic Protocellular Compartment FtsZ-Min System Dynamic Cleavage Constriction Modeler Run")
    target_specimen: str = Field(default="Cell-Free Microfluidic Giant Unilamellar Vesicle with Reconstituted FtsZ-FtsA and MinCDE Oscillatory Machinery")
    analytical_modality: str = Field(default="protocell-ftsz-cleavage-constriction")
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


class SyntheticCellDivisionFtszConstrictionStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    equatorial_constriction_pinching_force_pN: float
    min_protein_pole_to_pole_oscillation_period_s: float
    symmetric_daughter_vesicle_yield_pct: float
    ftsz_treadmilling_velocity_nm_per_s: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=SyntheticCellDivisionFtszConstrictionStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_synthetic_cell_division_ftsz_constriction(
    req: AnalyzeSyntheticCellDivisionFtszConstrictionRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Synthetic Protocellular Compartment FtsZ-Min System Dynamic Cleavage Constriction Modeler analysis and persist study."""
    engine = SyntheticCellDivisionFtszConstrictionEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SyntheticCellDivisionFtszConstrictionRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        equatorial_constriction_pinching_force_pN=result.equatorial_constriction_pinching_force_pN,
        min_protein_pole_to_pole_oscillation_period_s=result.min_protein_pole_to_pole_oscillation_period_s,
        symmetric_daughter_vesicle_yield_pct=result.symmetric_daughter_vesicle_yield_pct,
        ftsz_treadmilling_velocity_nm_per_s=result.ftsz_treadmilling_velocity_nm_per_s,
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

    return SyntheticCellDivisionFtszConstrictionStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        equatorial_constriction_pinching_force_pN=study.equatorial_constriction_pinching_force_pN,
        min_protein_pole_to_pole_oscillation_period_s=study.min_protein_pole_to_pole_oscillation_period_s,
        symmetric_daughter_vesicle_yield_pct=study.symmetric_daughter_vesicle_yield_pct,
        ftsz_treadmilling_velocity_nm_per_s=study.ftsz_treadmilling_velocity_nm_per_s,
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


@router.get("/studies", response_model=List[SyntheticCellDivisionFtszConstrictionStudyResponse])
async def list_synthetic_cell_division_ftsz_constriction_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Synthetic Protocellular Compartment FtsZ-Min System Dynamic Cleavage Constriction Modeler studies."""
    repo = SyntheticCellDivisionFtszConstrictionRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SyntheticCellDivisionFtszConstrictionStudyResponse)
async def get_synthetic_cell_division_ftsz_constriction_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Synthetic Protocellular Compartment FtsZ-Min System Dynamic Cleavage Constriction Modeler study by ID."""
    repo = SyntheticCellDivisionFtszConstrictionRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
