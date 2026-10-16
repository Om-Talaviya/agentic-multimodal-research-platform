"""FastAPI routes for Phase 551: Autonomous Engineered Magnetotactic Bacterial Magnetosome Nanowire Steering & Drug Cargo Transport Simulator."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.magnetotactic_bacterial_magnetosome_transport_repo import MagnetotacticBacterialMagnetosomeTransportRepository
from research.orchestration.magnetotactic_bacterial_magnetosome_transport_engine import MagnetotacticBacterialMagnetosomeTransportEngine

router = APIRouter(prefix="/magnetotactic-bacterial-magnetosome-transport", tags=["magnetotactic-bacterial-magnetosome-transport"])


class AnalyzeMagnetotacticBacterialMagnetosomeTransportRequest(BaseModel):
    name: str = Field(..., example="Autonomous Engineered Magnetotactic Bacterial Magnetosome Nanowire Steering & Drug Cargo Transport Simulator Run")
    target_specimen: str = Field(default="Engineered Magnetospirillum magneticum AMB-1 expressing Doxorubicin-Loaded Membrane Nanovesicles in Microfluidic Vascular Capillaries")
    analytical_modality: str = Field(default="bacterial-magnetosome-transport")
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


class MagnetotacticBacterialMagnetosomeTransportStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    magnetic_steering_velocity_um_s: float
    magnetosome_chain_magnetic_moment_femu: float
    tumor_microvascular_extravasation_rate_pct: float
    nanocarrier_drug_payload_delivery_ng_ml: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=MagnetotacticBacterialMagnetosomeTransportStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_magnetotactic_bacterial_magnetosome_transport(
    req: AnalyzeMagnetotacticBacterialMagnetosomeTransportRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Engineered Magnetotactic Bacterial Magnetosome Nanowire Steering & Drug Cargo Transport Simulator analysis and persist study."""
    engine = MagnetotacticBacterialMagnetosomeTransportEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = MagnetotacticBacterialMagnetosomeTransportRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        magnetic_steering_velocity_um_s=result.magnetic_steering_velocity_um_s,
        magnetosome_chain_magnetic_moment_femu=result.magnetosome_chain_magnetic_moment_femu,
        tumor_microvascular_extravasation_rate_pct=result.tumor_microvascular_extravasation_rate_pct,
        nanocarrier_drug_payload_delivery_ng_ml=result.nanocarrier_drug_payload_delivery_ng_ml,
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

    return MagnetotacticBacterialMagnetosomeTransportStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        magnetic_steering_velocity_um_s=study.magnetic_steering_velocity_um_s,
        magnetosome_chain_magnetic_moment_femu=study.magnetosome_chain_magnetic_moment_femu,
        tumor_microvascular_extravasation_rate_pct=study.tumor_microvascular_extravasation_rate_pct,
        nanocarrier_drug_payload_delivery_ng_ml=study.nanocarrier_drug_payload_delivery_ng_ml,
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


@router.get("/studies", response_model=List[MagnetotacticBacterialMagnetosomeTransportStudyResponse])
async def list_magnetotactic_bacterial_magnetosome_transport_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Engineered Magnetotactic Bacterial Magnetosome Nanowire Steering & Drug Cargo Transport Simulator studies."""
    repo = MagnetotacticBacterialMagnetosomeTransportRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=MagnetotacticBacterialMagnetosomeTransportStudyResponse)
async def get_magnetotactic_bacterial_magnetosome_transport_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Engineered Magnetotactic Bacterial Magnetosome Nanowire Steering & Drug Cargo Transport Simulator study by ID."""
    repo = MagnetotacticBacterialMagnetosomeTransportRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
