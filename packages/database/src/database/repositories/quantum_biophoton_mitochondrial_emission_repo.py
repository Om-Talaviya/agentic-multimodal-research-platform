"""Repository for Phase 509: Autonomous Ultra-Weak Biophoton Emission & Mitochondrial ROS Chemiluminescence Forecaster."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.quantum_biophoton_mitochondrial_emission import (
    QuantumBiophotonMitochondrialEmissionStudy,
    QuantumBiophotonMitochondrialEmissionItemProfile,
    QuantumBiophotonMitochondrialEmissionMetricTrace,
)


class QuantumBiophotonMitochondrialEmissionRepository:
    """Database operations for Autonomous Ultra-Weak Biophoton Emission & Mitochondrial ROS Chemiluminescence Forecaster."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Permeabilized Primary Cortical Neurons in Cryogenic Photomultiplier Chamber under Glutamate Stress",
        analytical_modality: str = "ultra-weak-biophoton-chemiluminescence",
        ultra_weak_photon_count_cps_per_cm2: float = 14.8,
        singlet_oxygen_decay_spectral_emission_nm: float = 1270.0,
        lipid_peroxy_chemiluminescence_quantum_yield: float = 8.5e-05,
        respiratory_chain_complex_leak_correlation: float = 0.912,
        confidence_score: float = 0.989,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> QuantumBiophotonMitochondrialEmissionStudy:
        study = QuantumBiophotonMitochondrialEmissionStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            ultra_weak_photon_count_cps_per_cm2=ultra_weak_photon_count_cps_per_cm2,
            singlet_oxygen_decay_spectral_emission_nm=singlet_oxygen_decay_spectral_emission_nm,
            lipid_peroxy_chemiluminescence_quantum_yield=lipid_peroxy_chemiluminescence_quantum_yield,
            respiratory_chain_complex_leak_correlation=respiratory_chain_complex_leak_correlation,
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
    ) -> QuantumBiophotonMitochondrialEmissionItemProfile:
        item = QuantumBiophotonMitochondrialEmissionItemProfile(
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
    ) -> QuantumBiophotonMitochondrialEmissionMetricTrace:
        trace = QuantumBiophotonMitochondrialEmissionMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[QuantumBiophotonMitochondrialEmissionStudy]:
        result = await self.session.execute(
            select(QuantumBiophotonMitochondrialEmissionStudy)
            .options(
                selectinload(QuantumBiophotonMitochondrialEmissionStudy.item_profiles),
                selectinload(QuantumBiophotonMitochondrialEmissionStudy.metric_traces),
            )
            .where(QuantumBiophotonMitochondrialEmissionStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[QuantumBiophotonMitochondrialEmissionStudy]:
        result = await self.session.execute(
            select(QuantumBiophotonMitochondrialEmissionStudy)
            .options(
                selectinload(QuantumBiophotonMitochondrialEmissionStudy.item_profiles),
                selectinload(QuantumBiophotonMitochondrialEmissionStudy.metric_traces),
            )
            .order_by(QuantumBiophotonMitochondrialEmissionStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
