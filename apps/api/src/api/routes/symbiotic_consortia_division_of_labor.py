"""FastAPI routes for Phase 464: Autonomous Synthetic Symbiotic Consortia Metabolic Division-of-Labor Population Dynamics Simulator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.symbiotic_consortia_division_of_labor_repo import SymbioticConsortiaDivisionOfLaborRepository
from research.orchestration.symbiotic_consortia_division_of_labor_engine import SymbioticConsortiaDivisionOfLaborEngine

router = APIRouter(prefix="/symbiotic-consortia-division-of-labor", tags=["symbiotic-consortia-division-of-labor"])


class AnalyzeSymbioticConsortiaDivisionOfLaborRequest(BaseModel):
    name: str = Field(..., example="Autonomous Synthetic Symbiotic Consortia Metabolic Division-of-Labor Population Dynamics Simulator Run")
    target_specimen: str = Field(default="Engineered E. coli and S. cerevisiae Cross-Feeding Co-Culture in Chemostat Bioreactor")
    analytical_modality: str = Field(default="symbiotic-metabolic-labor-dynamics")
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


class SymbioticConsortiaDivisionOfLaborStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    chemostat_steady_state_biomass_ratio: float
    cross_feeding_metabolite_exchange_flux_mmol_g_hr: float
    population_coexistence_lyapunov_exponent: float
    resource_utilization_synergy_factor: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=SymbioticConsortiaDivisionOfLaborStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_symbiotic_consortia_division_of_labor(
    req: AnalyzeSymbioticConsortiaDivisionOfLaborRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Synthetic Symbiotic Consortia Metabolic Division-of-Labor Population Dynamics Simulator analysis and persist study."""
    engine = SymbioticConsortiaDivisionOfLaborEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SymbioticConsortiaDivisionOfLaborRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        chemostat_steady_state_biomass_ratio=result.chemostat_steady_state_biomass_ratio,
        cross_feeding_metabolite_exchange_flux_mmol_g_hr=result.cross_feeding_metabolite_exchange_flux_mmol_g_hr,
        population_coexistence_lyapunov_exponent=result.population_coexistence_lyapunov_exponent,
        resource_utilization_synergy_factor=result.resource_utilization_synergy_factor,
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

    return SymbioticConsortiaDivisionOfLaborStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        chemostat_steady_state_biomass_ratio=study.chemostat_steady_state_biomass_ratio,
        cross_feeding_metabolite_exchange_flux_mmol_g_hr=study.cross_feeding_metabolite_exchange_flux_mmol_g_hr,
        population_coexistence_lyapunov_exponent=study.population_coexistence_lyapunov_exponent,
        resource_utilization_synergy_factor=study.resource_utilization_synergy_factor,
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


@router.get("/studies", response_model=List[SymbioticConsortiaDivisionOfLaborStudyResponse])
async def list_symbiotic_consortia_division_of_labor_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Synthetic Symbiotic Consortia Metabolic Division-of-Labor Population Dynamics Simulator studies."""
    repo = SymbioticConsortiaDivisionOfLaborRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SymbioticConsortiaDivisionOfLaborStudyResponse)
async def get_symbiotic_consortia_division_of_labor_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Synthetic Symbiotic Consortia Metabolic Division-of-Labor Population Dynamics Simulator study by ID."""
    repo = SymbioticConsortiaDivisionOfLaborRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
