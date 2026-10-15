"""FastAPI routes for Phase 534: Autonomous High-Throughput 3D Microfluidic Dielectrophoresis (DEP) Circulating Tumor Cell Sorter."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.microfluidic_cell_sorting_dielectrophoresis_repo import MicrofluidicCellSortingDielectrophoresisRepository
from research.orchestration.microfluidic_cell_sorting_dielectrophoresis_engine import MicrofluidicCellSortingDielectrophoresisEngine

router = APIRouter(prefix="/microfluidic-cell-sorting-dielectrophoresis", tags=["microfluidic-cell-sorting-dielectrophoresis"])


class AnalyzeMicrofluidicCellSortingDielectrophoresisRequest(BaseModel):
    name: str = Field(..., example="Autonomous High-Throughput 3D Microfluidic Dielectrophoresis (DEP) Circulating Tumor Cell Sorter Run")
    target_specimen: str = Field(default="Microfluidic Channel with 3D Quadrupole Electrodes for Label-Free Isolation of Metastatic Breast CTCs")
    analytical_modality: str = Field(default="microfluidic-dep-cell-sorting")
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


class MicrofluidicCellSortingDielectrophoresisStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    target_cell_recovery_purity_pct: float
    sorting_throughput_cells_per_s: float
    dielectrophoretic_crossover_frequency_khz: float
    post_sorting_cell_viability_pct: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=MicrofluidicCellSortingDielectrophoresisStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_microfluidic_cell_sorting_dielectrophoresis(
    req: AnalyzeMicrofluidicCellSortingDielectrophoresisRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous High-Throughput 3D Microfluidic Dielectrophoresis (DEP) Circulating Tumor Cell Sorter analysis and persist study."""
    engine = MicrofluidicCellSortingDielectrophoresisEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = MicrofluidicCellSortingDielectrophoresisRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        target_cell_recovery_purity_pct=result.target_cell_recovery_purity_pct,
        sorting_throughput_cells_per_s=result.sorting_throughput_cells_per_s,
        dielectrophoretic_crossover_frequency_khz=result.dielectrophoretic_crossover_frequency_khz,
        post_sorting_cell_viability_pct=result.post_sorting_cell_viability_pct,
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

    return MicrofluidicCellSortingDielectrophoresisStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        target_cell_recovery_purity_pct=study.target_cell_recovery_purity_pct,
        sorting_throughput_cells_per_s=study.sorting_throughput_cells_per_s,
        dielectrophoretic_crossover_frequency_khz=study.dielectrophoretic_crossover_frequency_khz,
        post_sorting_cell_viability_pct=study.post_sorting_cell_viability_pct,
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


@router.get("/studies", response_model=List[MicrofluidicCellSortingDielectrophoresisStudyResponse])
async def list_microfluidic_cell_sorting_dielectrophoresis_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous High-Throughput 3D Microfluidic Dielectrophoresis (DEP) Circulating Tumor Cell Sorter studies."""
    repo = MicrofluidicCellSortingDielectrophoresisRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=MicrofluidicCellSortingDielectrophoresisStudyResponse)
async def get_microfluidic_cell_sorting_dielectrophoresis_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous High-Throughput 3D Microfluidic Dielectrophoresis (DEP) Circulating Tumor Cell Sorter study by ID."""
    repo = MicrofluidicCellSortingDielectrophoresisRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
