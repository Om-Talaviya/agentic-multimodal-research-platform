"""Repository for Phase 538: Autonomous Non-Markovian Quantum Vibronic Resonance Exciton Energy Transfer Simulator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.photosynthetic_antenna_quantum_vibronic_coupling import (
    PhotosyntheticAntennaQuantumVibronicCouplingStudy,
    PhotosyntheticAntennaQuantumVibronicCouplingItemProfile,
    PhotosyntheticAntennaQuantumVibronicCouplingMetricTrace,
)


class PhotosyntheticAntennaQuantumVibronicCouplingRepository:
    """Database operations for Autonomous Non-Markovian Quantum Vibronic Resonance Exciton Energy Transfer Simulator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Light-Harvesting Complex II (LHCII) Trimer with 42 Chlorophyll Pigments embedded in Lipid Nanodisc",
        analytical_modality: str = "quantum-vibronic-exciton-dynamics",
        excitonic_energy_transfer_efficiency_pct: float = 98.6,
        quantum_coherence_dephasing_time_fs: float = 420.0,
        vibronic_resonance_coupling_cm_inv: float = 148.0,
        spectral_density_reorganization_energy_cm_inv: float = 65.0,
        confidence_score: float = 0.995,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> PhotosyntheticAntennaQuantumVibronicCouplingStudy:
        study = PhotosyntheticAntennaQuantumVibronicCouplingStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            excitonic_energy_transfer_efficiency_pct=excitonic_energy_transfer_efficiency_pct,
            quantum_coherence_dephasing_time_fs=quantum_coherence_dephasing_time_fs,
            vibronic_resonance_coupling_cm_inv=vibronic_resonance_coupling_cm_inv,
            spectral_density_reorganization_energy_cm_inv=spectral_density_reorganization_energy_cm_inv,
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
    ) -> PhotosyntheticAntennaQuantumVibronicCouplingItemProfile:
        item = PhotosyntheticAntennaQuantumVibronicCouplingItemProfile(
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
    ) -> PhotosyntheticAntennaQuantumVibronicCouplingMetricTrace:
        trace = PhotosyntheticAntennaQuantumVibronicCouplingMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[PhotosyntheticAntennaQuantumVibronicCouplingStudy]:
        stmt = (
            select(PhotosyntheticAntennaQuantumVibronicCouplingStudy)
            .where(PhotosyntheticAntennaQuantumVibronicCouplingStudy.id == study_id)
            .options(
                selectinload(PhotosyntheticAntennaQuantumVibronicCouplingStudy.item_profiles),
                selectinload(PhotosyntheticAntennaQuantumVibronicCouplingStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[PhotosyntheticAntennaQuantumVibronicCouplingStudy]:
        stmt = (
            select(PhotosyntheticAntennaQuantumVibronicCouplingStudy)
            .order_by(PhotosyntheticAntennaQuantumVibronicCouplingStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(PhotosyntheticAntennaQuantumVibronicCouplingStudy.item_profiles),
                selectinload(PhotosyntheticAntennaQuantumVibronicCouplingStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
