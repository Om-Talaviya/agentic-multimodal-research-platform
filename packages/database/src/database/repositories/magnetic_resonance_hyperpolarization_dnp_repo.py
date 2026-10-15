"""Repository for Phase 529: Autonomous Dissolution Dynamic Nuclear Polarization (DNP) Hyperpolarized Carbon-13 Flux Tracer."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.magnetic_resonance_hyperpolarization_dnp import (
    MagneticResonanceHyperpolarizationDnpStudy,
    MagneticResonanceHyperpolarizationDnpItemProfile,
    MagneticResonanceHyperpolarizationDnpMetricTrace,
)


class MagneticResonanceHyperpolarizationDnpRepository:
    """Database operations for Autonomous Dissolution Dynamic Nuclear Polarization (DNP) Hyperpolarized Carbon-13 Flux Tracer."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Hyperpolarized [1-13C] Pyruvate with Trityl Radical OX063 Polarized at 1.4K and 5T",
        analytical_modality: str = "dnp-hyperpolarized-nmr-flux",
        carbon_13_nuclear_polarization_pct: float = 46.8,
        in_vivo_t1_relaxation_time_s: float = 45.2,
        pyruvate_to_lactate_apparent_flux_rate_k_pl: float = 0.078,
        spectroscopic_snr_enhancement_factor: float = 14500.0,
        confidence_score: float = 0.995,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MagneticResonanceHyperpolarizationDnpStudy:
        study = MagneticResonanceHyperpolarizationDnpStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            carbon_13_nuclear_polarization_pct=carbon_13_nuclear_polarization_pct,
            in_vivo_t1_relaxation_time_s=in_vivo_t1_relaxation_time_s,
            pyruvate_to_lactate_apparent_flux_rate_k_pl=pyruvate_to_lactate_apparent_flux_rate_k_pl,
            spectroscopic_snr_enhancement_factor=spectroscopic_snr_enhancement_factor,
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
    ) -> MagneticResonanceHyperpolarizationDnpItemProfile:
        item = MagneticResonanceHyperpolarizationDnpItemProfile(
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
    ) -> MagneticResonanceHyperpolarizationDnpMetricTrace:
        trace = MagneticResonanceHyperpolarizationDnpMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MagneticResonanceHyperpolarizationDnpStudy]:
        stmt = (
            select(MagneticResonanceHyperpolarizationDnpStudy)
            .where(MagneticResonanceHyperpolarizationDnpStudy.id == study_id)
            .options(
                selectinload(MagneticResonanceHyperpolarizationDnpStudy.item_profiles),
                selectinload(MagneticResonanceHyperpolarizationDnpStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[MagneticResonanceHyperpolarizationDnpStudy]:
        stmt = (
            select(MagneticResonanceHyperpolarizationDnpStudy)
            .order_by(MagneticResonanceHyperpolarizationDnpStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(MagneticResonanceHyperpolarizationDnpStudy.item_profiles),
                selectinload(MagneticResonanceHyperpolarizationDnpStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
