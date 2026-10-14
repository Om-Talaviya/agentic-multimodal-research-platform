"""Repository for Phase 511: Autonomous In-Situ Cryo-ET Nuclear Envelope Lamina Meshwork & Mechanical Rigidity Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cryoet_nuclear_envelope_lamina_meshwork import (
    CryoetNuclearEnvelopeLaminaMeshworkStudy,
    CryoetNuclearEnvelopeLaminaMeshworkItemProfile,
    CryoetNuclearEnvelopeLaminaMeshworkMetricTrace,
)


class CryoetNuclearEnvelopeLaminaMeshworkRepository:
    """Database operations for Autonomous In-Situ Cryo-ET Nuclear Envelope Lamina Meshwork & Mechanical Rigidity Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Vitrified Fibroblast Nucleus Section with Lamin A/C Filamentous Intermediate Meshwork",
        analytical_modality: str = "cryoet-nuclear-envelope-lamina",
        lamin_filament_diameter_nm: float = 3.5,
        orthogonal_meshwork_pore_size_nm: float = 48.0,
        nuclear_membrane_elastic_modulus_kPa: float = 12.5,
        subtomogram_averaging_fsc_resolution_angstrom: float = 6.4,
        confidence_score: float = 0.992,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CryoetNuclearEnvelopeLaminaMeshworkStudy:
        study = CryoetNuclearEnvelopeLaminaMeshworkStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            lamin_filament_diameter_nm=lamin_filament_diameter_nm,
            orthogonal_meshwork_pore_size_nm=orthogonal_meshwork_pore_size_nm,
            nuclear_membrane_elastic_modulus_kPa=nuclear_membrane_elastic_modulus_kPa,
            subtomogram_averaging_fsc_resolution_angstrom=subtomogram_averaging_fsc_resolution_angstrom,
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
    ) -> CryoetNuclearEnvelopeLaminaMeshworkItemProfile:
        item = CryoetNuclearEnvelopeLaminaMeshworkItemProfile(
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
    ) -> CryoetNuclearEnvelopeLaminaMeshworkMetricTrace:
        trace = CryoetNuclearEnvelopeLaminaMeshworkMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CryoetNuclearEnvelopeLaminaMeshworkStudy]:
        result = await self.session.execute(
            select(CryoetNuclearEnvelopeLaminaMeshworkStudy)
            .options(
                selectinload(CryoetNuclearEnvelopeLaminaMeshworkStudy.item_profiles),
                selectinload(CryoetNuclearEnvelopeLaminaMeshworkStudy.metric_traces),
            )
            .where(CryoetNuclearEnvelopeLaminaMeshworkStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[CryoetNuclearEnvelopeLaminaMeshworkStudy]:
        result = await self.session.execute(
            select(CryoetNuclearEnvelopeLaminaMeshworkStudy)
            .options(
                selectinload(CryoetNuclearEnvelopeLaminaMeshworkStudy.item_profiles),
                selectinload(CryoetNuclearEnvelopeLaminaMeshworkStudy.metric_traces),
            )
            .order_by(CryoetNuclearEnvelopeLaminaMeshworkStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
