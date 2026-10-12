"""FastAPI routes for Phase 437: Autonomous Microbial Electrogenic Biofilm Extracellular Electron Transfer (EET) Simulator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.microbial_electrogenic_biofilm_flux_repo import MicrobialElectrogenicBiofilmRepository
from research.orchestration.microbial_electrogenic_biofilm_flux_engine import MicrobialElectrogenicBiofilmEngine

router = APIRouter(prefix="/microbial-electrogenic-biofilm", tags=["microbial-electrogenic-biofilm"])


class AnalyzeMicrobialElectrogenicBiofilmRequest(BaseModel):
    name: str = Field(..., example="Autonomous Microbial Electrogenic Biofilm Extracellular Electron Transfer (EET) Simulator Run")
    target_specimen: str = Field(default="Shewanella oneidensis MR-1 Anode Biofilm with Multi-Heme Cytochrome Array")
    analytical_modality: str = Field(default="microbial-eet-biofilm")
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


class MicrobialElectrogenicBiofilmStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    current_density_mA_per_cm2: float
    cytochrome_conduction_rate_electrons_per_s: float
    redox_potential_gradient_mV: float
    biofilm_coulombic_efficiency: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=MicrobialElectrogenicBiofilmStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_microbial_electrogenic_biofilm_flux(
    req: AnalyzeMicrobialElectrogenicBiofilmRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Microbial Electrogenic Biofilm Extracellular Electron Transfer (EET) Simulator analysis and persist study."""
    engine = MicrobialElectrogenicBiofilmEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = MicrobialElectrogenicBiofilmRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        current_density_mA_per_cm2=result.current_density_mA_per_cm2,
        cytochrome_conduction_rate_electrons_per_s=result.cytochrome_conduction_rate_electrons_per_s,
        redox_potential_gradient_mV=result.redox_potential_gradient_mV,
        biofilm_coulombic_efficiency=result.biofilm_coulombic_efficiency,
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

    return MicrobialElectrogenicBiofilmStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        current_density_mA_per_cm2=study.current_density_mA_per_cm2,
        cytochrome_conduction_rate_electrons_per_s=study.cytochrome_conduction_rate_electrons_per_s,
        redox_potential_gradient_mV=study.redox_potential_gradient_mV,
        biofilm_coulombic_efficiency=study.biofilm_coulombic_efficiency,
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


@router.get("/studies", response_model=List[MicrobialElectrogenicBiofilmStudyResponse])
async def list_microbial_electrogenic_biofilm_flux_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Microbial Electrogenic Biofilm Extracellular Electron Transfer (EET) Simulator studies."""
    repo = MicrobialElectrogenicBiofilmRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=MicrobialElectrogenicBiofilmStudyResponse)
async def get_microbial_electrogenic_biofilm_flux_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Microbial Electrogenic Biofilm Extracellular Electron Transfer (EET) Simulator study by ID."""
    repo = MicrobialElectrogenicBiofilmRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
