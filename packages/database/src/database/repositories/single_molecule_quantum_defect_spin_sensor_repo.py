"""Repository for Phase 540: Autonomous Diamond Nitrogen-Vacancy (NV) Center Quantum Defect Intracellular Thermal & Magnetic Sensor."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.single_molecule_quantum_defect_spin_sensor import (
    SingleMoleculeQuantumDefectSpinSensorStudy,
    SingleMoleculeQuantumDefectSpinSensorItemProfile,
    SingleMoleculeQuantumDefectSpinSensorMetricTrace,
)


class SingleMoleculeQuantumDefectSpinSensorRepository:
    """Database operations for Autonomous Diamond Nitrogen-Vacancy (NV) Center Quantum Defect Intracellular Thermal & Magnetic Sensor."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Fluorescent Nanodiamond with Single NV- Spin Defect internalized in Living Single Macrophage Cell",
        analytical_modality: str = "nv-center-quantum-sensing",
        magnetic_field_sensitivity_nT_sqrt_hz: float = 12.4,
        intracellular_thermal_sensitivity_mK_sqrt_hz: float = 45.0,
        spin_coherence_time_t2_us: float = 185.0,
        odmr_spectral_contrast_pct: float = 14.8,
        confidence_score: float = 0.996,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SingleMoleculeQuantumDefectSpinSensorStudy:
        study = SingleMoleculeQuantumDefectSpinSensorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            magnetic_field_sensitivity_nT_sqrt_hz=magnetic_field_sensitivity_nT_sqrt_hz,
            intracellular_thermal_sensitivity_mK_sqrt_hz=intracellular_thermal_sensitivity_mK_sqrt_hz,
            spin_coherence_time_t2_us=spin_coherence_time_t2_us,
            odmr_spectral_contrast_pct=odmr_spectral_contrast_pct,
            confidence_score=confidence_score,
            status=status,
            parameters=parameters or {},
            summary_report=summary_report,
        )
        self.session.add(study)
        await self.session.flush()
        await self.session.refresh(study)
        return study

    async def add_item_profile(
        self,
        study_id: UUID,
        item_name: str,
        profile_category: str = "Analysis Profile",
        quantitative_value: float = 1.0,
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> SingleMoleculeQuantumDefectSpinSensorItemProfile:
        item = SingleMoleculeQuantumDefectSpinSensorItemProfile(
            study_id=study_id,
            item_name=item_name,
            profile_category=profile_category,
            quantitative_value=quantitative_value,
            log2_fold_change=log2_fold_change,
            significance_score=significance_score,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def add_metric_trace(
        self,
        study_id: UUID,
        metric_dimension: str,
        observed_value: float,
        z_score: float = 0.0,
        p_value: float = 0.05,
    ) -> SingleMoleculeQuantumDefectSpinSensorMetricTrace:
        trace = SingleMoleculeQuantumDefectSpinSensorMetricTrace(
            study_id=study_id,
            metric_dimension=metric_dimension,
            observed_value=observed_value,
            z_score=z_score,
            p_value=p_value,
        )
        self.session.add(trace)
        await self.session.flush()
        await self.session.refresh(trace)
        return trace

    async def get_study(self, study_id: UUID) -> Optional[SingleMoleculeQuantumDefectSpinSensorStudy]:
        stmt = (
            select(SingleMoleculeQuantumDefectSpinSensorStudy)
            .where(SingleMoleculeQuantumDefectSpinSensorStudy.id == study_id)
            .options(
                selectinload(SingleMoleculeQuantumDefectSpinSensorStudy.item_profiles),
                selectinload(SingleMoleculeQuantumDefectSpinSensorStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[SingleMoleculeQuantumDefectSpinSensorStudy]:
        stmt = (
            select(SingleMoleculeQuantumDefectSpinSensorStudy)
            .order_by(SingleMoleculeQuantumDefectSpinSensorStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(SingleMoleculeQuantumDefectSpinSensorStudy.item_profiles),
                selectinload(SingleMoleculeQuantumDefectSpinSensorStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
