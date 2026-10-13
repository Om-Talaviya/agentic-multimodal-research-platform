"""FastAPI routes for Phase 459: Autonomous Synthetic Multicellular Planar Cell Polarity (PCP) Asymmetric Segregation Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.multicellular_planar_cell_polarity_repo import MulticellularPlanarCellPolarityRepository
from research.orchestration.multicellular_planar_cell_polarity_engine import MulticellularPlanarCellPolarityEngine

router = APIRouter(prefix="/multicellular-planar-cell-polarity", tags=["multicellular-planar-cell-polarity"])


class AnalyzeMulticellularPlanarCellPolarityRequest(BaseModel):
    name: str = Field(..., example="Autonomous Synthetic Multicellular Planar Cell Polarity (PCP) Asymmetric Segregation Engine Run")
    target_specimen: str = Field(default="Engineered Epithelial Monolayer with Frizzled-6/Vangl2 Core Protein Polarized Ensembles")
    analytical_modality: str = Field(default="planar-cell-polarity-segregation")
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


class MulticellularPlanarCellPolarityStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    asymmetric_crescent_enrichment_ratio: float
    nematic_order_director_coherence: float
    junctional_remodeling_strain_rate_per_hr: float
    global_polarization_vector_magnitude: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=MulticellularPlanarCellPolarityStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_multicellular_planar_cell_polarity(
    req: AnalyzeMulticellularPlanarCellPolarityRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Synthetic Multicellular Planar Cell Polarity (PCP) Asymmetric Segregation Engine analysis and persist study."""
    engine = MulticellularPlanarCellPolarityEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = MulticellularPlanarCellPolarityRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        asymmetric_crescent_enrichment_ratio=result.asymmetric_crescent_enrichment_ratio,
        nematic_order_director_coherence=result.nematic_order_director_coherence,
        junctional_remodeling_strain_rate_per_hr=result.junctional_remodeling_strain_rate_per_hr,
        global_polarization_vector_magnitude=result.global_polarization_vector_magnitude,
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

    return MulticellularPlanarCellPolarityStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        asymmetric_crescent_enrichment_ratio=study.asymmetric_crescent_enrichment_ratio,
        nematic_order_director_coherence=study.nematic_order_director_coherence,
        junctional_remodeling_strain_rate_per_hr=study.junctional_remodeling_strain_rate_per_hr,
        global_polarization_vector_magnitude=study.global_polarization_vector_magnitude,
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


@router.get("/studies", response_model=List[MulticellularPlanarCellPolarityStudyResponse])
async def list_multicellular_planar_cell_polarity_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Synthetic Multicellular Planar Cell Polarity (PCP) Asymmetric Segregation Engine studies."""
    repo = MulticellularPlanarCellPolarityRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=MulticellularPlanarCellPolarityStudyResponse)
async def get_multicellular_planar_cell_polarity_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Synthetic Multicellular Planar Cell Polarity (PCP) Asymmetric Segregation Engine study by ID."""
    repo = MulticellularPlanarCellPolarityRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
