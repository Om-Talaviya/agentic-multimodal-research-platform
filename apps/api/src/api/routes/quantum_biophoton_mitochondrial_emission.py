"""FastAPI routes for Phase 509: Autonomous Ultra-Weak Biophoton Emission & Mitochondrial ROS Chemiluminescence Forecaster."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.quantum_biophoton_mitochondrial_emission_repo import QuantumBiophotonMitochondrialEmissionRepository
from research.orchestration.quantum_biophoton_mitochondrial_emission_engine import QuantumBiophotonMitochondrialEmissionEngine

router = APIRouter(prefix="/quantum-biophoton-mitochondrial-emission", tags=["quantum-biophoton-mitochondrial-emission"])


class AnalyzeQuantumBiophotonMitochondrialEmissionRequest(BaseModel):
    name: str = Field(..., example="Autonomous Ultra-Weak Biophoton Emission & Mitochondrial ROS Chemiluminescence Forecaster Run")
    target_specimen: str = Field(default="Permeabilized Primary Cortical Neurons in Cryogenic Photomultiplier Chamber under Glutamate Stress")
    analytical_modality: str = Field(default="ultra-weak-biophoton-chemiluminescence")
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


class QuantumBiophotonMitochondrialEmissionStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    ultra_weak_photon_count_cps_per_cm2: float
    singlet_oxygen_decay_spectral_emission_nm: float
    lipid_peroxy_chemiluminescence_quantum_yield: float
    respiratory_chain_complex_leak_correlation: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=QuantumBiophotonMitochondrialEmissionStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_quantum_biophoton_mitochondrial_emission(
    req: AnalyzeQuantumBiophotonMitochondrialEmissionRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Ultra-Weak Biophoton Emission & Mitochondrial ROS Chemiluminescence Forecaster analysis and persist study."""
    engine = QuantumBiophotonMitochondrialEmissionEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = QuantumBiophotonMitochondrialEmissionRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        ultra_weak_photon_count_cps_per_cm2=result.ultra_weak_photon_count_cps_per_cm2,
        singlet_oxygen_decay_spectral_emission_nm=result.singlet_oxygen_decay_spectral_emission_nm,
        lipid_peroxy_chemiluminescence_quantum_yield=result.lipid_peroxy_chemiluminescence_quantum_yield,
        respiratory_chain_complex_leak_correlation=result.respiratory_chain_complex_leak_correlation,
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

    return QuantumBiophotonMitochondrialEmissionStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        ultra_weak_photon_count_cps_per_cm2=study.ultra_weak_photon_count_cps_per_cm2,
        singlet_oxygen_decay_spectral_emission_nm=study.singlet_oxygen_decay_spectral_emission_nm,
        lipid_peroxy_chemiluminescence_quantum_yield=study.lipid_peroxy_chemiluminescence_quantum_yield,
        respiratory_chain_complex_leak_correlation=study.respiratory_chain_complex_leak_correlation,
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


@router.get("/studies", response_model=List[QuantumBiophotonMitochondrialEmissionStudyResponse])
async def list_quantum_biophoton_mitochondrial_emission_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Ultra-Weak Biophoton Emission & Mitochondrial ROS Chemiluminescence Forecaster studies."""
    repo = QuantumBiophotonMitochondrialEmissionRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=QuantumBiophotonMitochondrialEmissionStudyResponse)
async def get_quantum_biophoton_mitochondrial_emission_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Ultra-Weak Biophoton Emission & Mitochondrial ROS Chemiluminescence Forecaster study by ID."""
    repo = QuantumBiophotonMitochondrialEmissionRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
