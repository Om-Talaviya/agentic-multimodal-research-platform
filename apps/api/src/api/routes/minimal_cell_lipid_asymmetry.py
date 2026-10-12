"""FastAPI routes for Phase 423: Autonomous Synthetic Minimal Cell Membrane Lipid Bilayer Asymmetry & Vesicle Budding Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.minimal_cell_lipid_asymmetry_repo import MinimalCellLipidAsymmetryRepository
from research.orchestration.minimal_cell_lipid_asymmetry_engine import MinimalCellLipidAsymmetryEngine

router = APIRouter(prefix="/minimal-cell-lipid-asymmetry", tags=["minimal-cell-lipid-asymmetry"])


class AnalyzeMinimalCellLipidAsymmetryRequest(BaseModel):
    name: str = Field(..., example="Autonomous Synthetic Minimal Cell Membrane Lipid Bilayer Asymmetry & Vesicle Budding Engine Run")
    target_specimen: str = Field(default="Synthetic Giant Unilamellar Vesicle (GUV) with Flippase ABCB4")
    analytical_modality: str = Field(default="minimal-cell-lipid")
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


class MinimalCellLipidAsymmetryStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    bilayer_asymmetry_index: float
    membrane_bending_rigidity_kbt: float
    vesicle_budding_rate_um_per_min: float
    inner_leaflet_phosphatidylserine_ratio: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=MinimalCellLipidAsymmetryStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_minimal_cell_lipid_asymmetry(
    req: AnalyzeMinimalCellLipidAsymmetryRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Synthetic Minimal Cell Membrane Lipid Bilayer Asymmetry & Vesicle Budding Engine analysis and persist study."""
    engine = MinimalCellLipidAsymmetryEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = MinimalCellLipidAsymmetryRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        bilayer_asymmetry_index=result.bilayer_asymmetry_index,
        membrane_bending_rigidity_kbt=result.membrane_bending_rigidity_kbt,
        vesicle_budding_rate_um_per_min=result.vesicle_budding_rate_um_per_min,
        inner_leaflet_phosphatidylserine_ratio=result.inner_leaflet_phosphatidylserine_ratio,
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

    return MinimalCellLipidAsymmetryStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        bilayer_asymmetry_index=study.bilayer_asymmetry_index,
        membrane_bending_rigidity_kbt=study.membrane_bending_rigidity_kbt,
        vesicle_budding_rate_um_per_min=study.vesicle_budding_rate_um_per_min,
        inner_leaflet_phosphatidylserine_ratio=study.inner_leaflet_phosphatidylserine_ratio,
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


@router.get("/studies", response_model=List[MinimalCellLipidAsymmetryStudyResponse])
async def list_minimal_cell_lipid_asymmetry_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Synthetic Minimal Cell Membrane Lipid Bilayer Asymmetry & Vesicle Budding Engine studies."""
    repo = MinimalCellLipidAsymmetryRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=MinimalCellLipidAsymmetryStudyResponse)
async def get_minimal_cell_lipid_asymmetry_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Synthetic Minimal Cell Membrane Lipid Bilayer Asymmetry & Vesicle Budding Engine study by ID."""
    repo = MinimalCellLipidAsymmetryRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
