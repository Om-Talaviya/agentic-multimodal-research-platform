"""Repository for Phase 426: Autonomous Mass Photometry Macromolecular Oligomeric Mass Distribution & Dissociation Constant (KD) Estimator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.mass_photometry_oligomer_kd import (
    MassPhotometryOligomerKdStudy,
    MassPhotometryOligomerKdItemProfile,
    MassPhotometryOligomerKdMetricTrace,
)


class MassPhotometryOligomerKdRepository:
    """Database operations for Autonomous Mass Photometry Macromolecular Oligomeric Mass Distribution & Dissociation Constant (KD) Estimator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Native Macromolecular Assembly on Glass Coverslip Surface",
        analytical_modality: str = "mass-photometry-kd",
        molecular_mass_kda: float = 148.5,
        equilibrium_dissociation_constant_nM: float = 18.4,
        dimer_to_monomer_peak_ratio: float = 2.85,
        contrast_interferometry_snr: float = 42.6,
        confidence_score: float = 0.992,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MassPhotometryOligomerKdStudy:
        study = MassPhotometryOligomerKdStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            molecular_mass_kda=molecular_mass_kda,
            equilibrium_dissociation_constant_nM=equilibrium_dissociation_constant_nM,
            dimer_to_monomer_peak_ratio=dimer_to_monomer_peak_ratio,
            contrast_interferometry_snr=contrast_interferometry_snr,
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
    ) -> MassPhotometryOligomerKdItemProfile:
        item = MassPhotometryOligomerKdItemProfile(
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
    ) -> MassPhotometryOligomerKdMetricTrace:
        trace = MassPhotometryOligomerKdMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MassPhotometryOligomerKdStudy]:
        result = await self.session.execute(
            select(MassPhotometryOligomerKdStudy)
            .options(
                selectinload(MassPhotometryOligomerKdStudy.item_profiles),
                selectinload(MassPhotometryOligomerKdStudy.metric_traces),
            )
            .where(MassPhotometryOligomerKdStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[MassPhotometryOligomerKdStudy]:
        result = await self.session.execute(
            select(MassPhotometryOligomerKdStudy)
            .options(
                selectinload(MassPhotometryOligomerKdStudy.item_profiles),
                selectinload(MassPhotometryOligomerKdStudy.metric_traces),
            )
            .order_by(MassPhotometryOligomerKdStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
