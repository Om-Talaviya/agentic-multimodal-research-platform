"""FastAPI routes for Phase 530: Autonomous Bacterial Outer Membrane Vesicle (OMV) Biogenesis & Cargo Sorting Predictor."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.bacterial_outer_membrane_vesicle_packaging_repo import BacterialOuterMembraneVesiclePackagingRepository
from research.orchestration.bacterial_outer_membrane_vesicle_packaging_engine import BacterialOuterMembraneVesiclePackagingEngine

router = APIRouter(prefix="/bacterial-outer-membrane-vesicle-packaging", tags=["bacterial-outer-membrane-vesicle-packaging"])


class AnalyzeBacterialOuterMembraneVesiclePackagingRequest(BaseModel):
    name: str = Field(..., example="Autonomous Bacterial Outer Membrane Vesicle (OMV) Biogenesis & Cargo Sorting Predictor Run")
    target_specimen: str = Field(default="Hyper-Vesiculating Engineered Pseudomonas aeruginosa Strain PAO1 Membrane Fractions")
    analytical_modality: str = Field(default="omv-biogenesis-cargo-sorting")
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


class BacterialOuterMembraneVesiclePackagingStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    vesiculation_rate_omv_per_cell_hr: float
    cargo_virulence_factor_enrichment_ratio: float
    vesicle_average_hydrodynamic_diameter_nm: float
    lps_phospholipid_asymmetry_index: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=BacterialOuterMembraneVesiclePackagingStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_bacterial_outer_membrane_vesicle_packaging(
    req: AnalyzeBacterialOuterMembraneVesiclePackagingRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Bacterial Outer Membrane Vesicle (OMV) Biogenesis & Cargo Sorting Predictor analysis and persist study."""
    engine = BacterialOuterMembraneVesiclePackagingEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = BacterialOuterMembraneVesiclePackagingRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        vesiculation_rate_omv_per_cell_hr=result.vesiculation_rate_omv_per_cell_hr,
        cargo_virulence_factor_enrichment_ratio=result.cargo_virulence_factor_enrichment_ratio,
        vesicle_average_hydrodynamic_diameter_nm=result.vesicle_average_hydrodynamic_diameter_nm,
        lps_phospholipid_asymmetry_index=result.lps_phospholipid_asymmetry_index,
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

    return BacterialOuterMembraneVesiclePackagingStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        vesiculation_rate_omv_per_cell_hr=study.vesiculation_rate_omv_per_cell_hr,
        cargo_virulence_factor_enrichment_ratio=study.cargo_virulence_factor_enrichment_ratio,
        vesicle_average_hydrodynamic_diameter_nm=study.vesicle_average_hydrodynamic_diameter_nm,
        lps_phospholipid_asymmetry_index=study.lps_phospholipid_asymmetry_index,
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


@router.get("/studies", response_model=List[BacterialOuterMembraneVesiclePackagingStudyResponse])
async def list_bacterial_outer_membrane_vesicle_packaging_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Bacterial Outer Membrane Vesicle (OMV) Biogenesis & Cargo Sorting Predictor studies."""
    repo = BacterialOuterMembraneVesiclePackagingRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=BacterialOuterMembraneVesiclePackagingStudyResponse)
async def get_bacterial_outer_membrane_vesicle_packaging_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Bacterial Outer Membrane Vesicle (OMV) Biogenesis & Cargo Sorting Predictor study by ID."""
    repo = BacterialOuterMembraneVesiclePackagingRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
