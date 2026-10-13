"""FastAPI routes for Phase 462: Autonomous Living Biomaterial Engineered Bacterial Cellulose Scaffold Cross-Linking Engine."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.bacterial_cellulose_scaffold_crosslinking_repo import BacterialCelluloseScaffoldRepository
from research.orchestration.bacterial_cellulose_scaffold_crosslinking_engine import BacterialCelluloseScaffoldEngine

router = APIRouter(prefix="/bacterial-cellulose-scaffold", tags=["bacterial-cellulose-scaffold"])


class AnalyzeBacterialCelluloseScaffoldRequest(BaseModel):
    name: str = Field(..., example="Autonomous Living Biomaterial Engineered Bacterial Cellulose Scaffold Cross-Linking Engine Run")
    target_specimen: str = Field(default="Komagataeibacter xylinus Pellicle Hydrogel with Genetically Encoded SpyTag/SpyCatcher Nodes")
    analytical_modality: str = Field(default="living-bacterial-cellulose")
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


class BacterialCelluloseScaffoldStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    youngs_elastic_modulus_megapascals: float
    microfibril_crystallinity_index: float
    tensile_fracture_toughness_kj_per_m2: float
    water_retention_swelling_ratio: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=BacterialCelluloseScaffoldStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_bacterial_cellulose_scaffold_crosslinking(
    req: AnalyzeBacterialCelluloseScaffoldRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Living Biomaterial Engineered Bacterial Cellulose Scaffold Cross-Linking Engine analysis and persist study."""
    engine = BacterialCelluloseScaffoldEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = BacterialCelluloseScaffoldRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        youngs_elastic_modulus_megapascals=result.youngs_elastic_modulus_megapascals,
        microfibril_crystallinity_index=result.microfibril_crystallinity_index,
        tensile_fracture_toughness_kj_per_m2=result.tensile_fracture_toughness_kj_per_m2,
        water_retention_swelling_ratio=result.water_retention_swelling_ratio,
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

    return BacterialCelluloseScaffoldStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        youngs_elastic_modulus_megapascals=study.youngs_elastic_modulus_megapascals,
        microfibril_crystallinity_index=study.microfibril_crystallinity_index,
        tensile_fracture_toughness_kj_per_m2=study.tensile_fracture_toughness_kj_per_m2,
        water_retention_swelling_ratio=study.water_retention_swelling_ratio,
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


@router.get("/studies", response_model=List[BacterialCelluloseScaffoldStudyResponse])
async def list_bacterial_cellulose_scaffold_crosslinking_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Living Biomaterial Engineered Bacterial Cellulose Scaffold Cross-Linking Engine studies."""
    repo = BacterialCelluloseScaffoldRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=BacterialCelluloseScaffoldStudyResponse)
async def get_bacterial_cellulose_scaffold_crosslinking_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Living Biomaterial Engineered Bacterial Cellulose Scaffold Cross-Linking Engine study by ID."""
    repo = BacterialCelluloseScaffoldRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
