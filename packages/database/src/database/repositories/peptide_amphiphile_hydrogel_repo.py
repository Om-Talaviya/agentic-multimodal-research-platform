"""Repository for Phase 369: Autonomous Self-Assembling Peptide Amphiphile Supramolecular Hydrogel Nanofiber Matrix Modeler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.peptide_amphiphile_hydrogel import (
    PeptideAmphiphileHydrogelStudy,
    PeptideAmphiphileHydrogelItemProfile,
    PeptideAmphiphileHydrogelMetricTrace,
)


class PeptideAmphiphileHydrogelRepository:
    """Database operations for Autonomous Self-Assembling Peptide Amphiphile Supramolecular Hydrogel Nanofiber Matrix Modeler studies."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human Patient Cohort Sample",
        analytical_modality: str = "peptide-amphiphile-hydrogel",
        nanofiber_youngs_modulus_elastic_storage_g_prime_pa: float = 1850.0,
        neurite_outgrowth_extension_rate_um_day: float = 145.0,
        confidence_score: float = 0.985,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> PeptideAmphiphileHydrogelStudy:
        study = PeptideAmphiphileHydrogelStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            nanofiber_youngs_modulus_elastic_storage_g_prime_pa=nanofiber_youngs_modulus_elastic_storage_g_prime_pa,
            neurite_outgrowth_extension_rate_um_day=neurite_outgrowth_extension_rate_um_day,
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
        profile_category: str = "Primary Target",
        quantitative_value: float = 100.0,
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> PeptideAmphiphileHydrogelItemProfile:
        item = PeptideAmphiphileHydrogelItemProfile(
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
        z_score: float = 2.1,
        p_value: float = 0.001,
    ) -> PeptideAmphiphileHydrogelMetricTrace:
        item = PeptideAmphiphileHydrogelMetricTrace(
            study_id=study_id,
            metric_dimension=metric_dimension,
            observed_value=observed_value,
            z_score=z_score,
            p_value=p_value,
        )
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def get_study(self, study_id: UUID) -> Optional[PeptideAmphiphileHydrogelStudy]:
        stmt = select(PeptideAmphiphileHydrogelStudy).where(PeptideAmphiphileHydrogelStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[PeptideAmphiphileHydrogelStudy]:
        stmt = select(PeptideAmphiphileHydrogelStudy).order_by(PeptideAmphiphileHydrogelStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
