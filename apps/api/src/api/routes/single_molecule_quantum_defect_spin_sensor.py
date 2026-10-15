"""FastAPI routes for Phase 540: Autonomous Diamond Nitrogen-Vacancy (NV) Center Quantum Defect Intracellular Thermal & Magnetic Sensor."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db_session
from database.repositories.single_molecule_quantum_defect_spin_sensor_repo import SingleMoleculeQuantumDefectSpinSensorRepository
from research.orchestration.single_molecule_quantum_defect_spin_sensor_engine import SingleMoleculeQuantumDefectSpinSensorEngine

router = APIRouter(prefix="/single-molecule-quantum-defect-spin-sensor", tags=["single-molecule-quantum-defect-spin-sensor"])


class AnalyzeSingleMoleculeQuantumDefectSpinSensorRequest(BaseModel):
    name: str = Field(..., example="Autonomous Diamond Nitrogen-Vacancy (NV) Center Quantum Defect Intracellular Thermal & Magnetic Sensor Run")
    target_specimen: str = Field(default="Fluorescent Nanodiamond with Single NV- Spin Defect internalized in Living Single Macrophage Cell")
    analytical_modality: str = Field(default="nv-center-quantum-sensing")
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


class SingleMoleculeQuantumDefectSpinSensorStudyResponse(BaseModel):
    id: UUID
    name: str
    target_specimen: str
    analytical_modality: str
    magnetic_field_sensitivity_nT_sqrt_hz: float
    intracellular_thermal_sensitivity_mK_sqrt_hz: float
    spin_coherence_time_t2_us: float
    odmr_spectral_contrast_pct: float
    confidence_score: float
    status: str
    summary_report: Optional[str]
    item_profiles: List[ItemProfileResponse] = []
    metric_traces: List[MetricTraceResponse] = []

    class Config:
        from_attributes = True


@router.post("/analyze", response_model=SingleMoleculeQuantumDefectSpinSensorStudyResponse, status_code=status.HTTP_201_CREATED)
async def analyze_single_molecule_quantum_defect_spin_sensor(
    req: AnalyzeSingleMoleculeQuantumDefectSpinSensorRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Run autonomous Autonomous Diamond Nitrogen-Vacancy (NV) Center Quantum Defect Intracellular Thermal & Magnetic Sensor analysis and persist study."""
    engine = SingleMoleculeQuantumDefectSpinSensorEngine()
    result = engine.analyze(
        target_specimen=req.target_specimen,
        analytical_modality=req.analytical_modality,
        input_scale=req.input_scale,
    )

    repo = SingleMoleculeQuantumDefectSpinSensorRepository(session)
    study = await repo.create_study(
        name=req.name,
        target_specimen=result.target_specimen,
        analytical_modality=result.analytical_modality,
        magnetic_field_sensitivity_nT_sqrt_hz=result.magnetic_field_sensitivity_nT_sqrt_hz,
        intracellular_thermal_sensitivity_mK_sqrt_hz=result.intracellular_thermal_sensitivity_mK_sqrt_hz,
        spin_coherence_time_t2_us=result.spin_coherence_time_t2_us,
        odmr_spectral_contrast_pct=result.odmr_spectral_contrast_pct,
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

    return SingleMoleculeQuantumDefectSpinSensorStudyResponse(
        id=study.id,
        name=study.name,
        target_specimen=study.target_specimen,
        analytical_modality=study.analytical_modality,
        magnetic_field_sensitivity_nT_sqrt_hz=study.magnetic_field_sensitivity_nT_sqrt_hz,
        intracellular_thermal_sensitivity_mK_sqrt_hz=study.intracellular_thermal_sensitivity_mK_sqrt_hz,
        spin_coherence_time_t2_us=study.spin_coherence_time_t2_us,
        odmr_spectral_contrast_pct=study.odmr_spectral_contrast_pct,
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


@router.get("/studies", response_model=List[SingleMoleculeQuantumDefectSpinSensorStudyResponse])
async def list_single_molecule_quantum_defect_spin_sensor_studies(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    """List recent Autonomous Diamond Nitrogen-Vacancy (NV) Center Quantum Defect Intracellular Thermal & Magnetic Sensor studies."""
    repo = SingleMoleculeQuantumDefectSpinSensorRepository(session)
    return await repo.list_studies(limit=limit)


@router.get("/studies/{study_id}", response_model=SingleMoleculeQuantumDefectSpinSensorStudyResponse)
async def get_single_molecule_quantum_defect_spin_sensor_study(
    study_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    """Fetch specific Autonomous Diamond Nitrogen-Vacancy (NV) Center Quantum Defect Intracellular Thermal & Magnetic Sensor study by ID."""
    repo = SingleMoleculeQuantumDefectSpinSensorRepository(session)
    study = await repo.get_study(study_id)
    if not study:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study {study_id} not found",
        )
    return study
