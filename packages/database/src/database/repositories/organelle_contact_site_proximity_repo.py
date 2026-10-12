"""Repository for Phase 429: Autonomous Whole-Cell Organelle Contact Site & Membrane Proximity Distance Transformer."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.organelle_contact_site_proximity import (
    OrganelleContactSiteProximityStudy,
    OrganelleContactSiteProximityItemProfile,
    OrganelleContactSiteProximityMetricTrace,
)


class OrganelleContactSiteProximityRepository:
    """Database operations for Autonomous Whole-Cell Organelle Contact Site & Membrane Proximity Distance Transformer."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Focused Ion Beam Scanning Electron Microscopy (FIB-SEM) Whole Cell",
        analytical_modality: str = "organelle-contact-site",
        er_mitochondria_contact_distance_nm: float = 14.2,
        contact_site_surface_area_um2: float = 2.85,
        lipid_transfer_flux_rate: float = 125.0,
        organelle_tethering_density: float = 0.892,
        confidence_score: float = 0.99,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> OrganelleContactSiteProximityStudy:
        study = OrganelleContactSiteProximityStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            er_mitochondria_contact_distance_nm=er_mitochondria_contact_distance_nm,
            contact_site_surface_area_um2=contact_site_surface_area_um2,
            lipid_transfer_flux_rate=lipid_transfer_flux_rate,
            organelle_tethering_density=organelle_tethering_density,
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
    ) -> OrganelleContactSiteProximityItemProfile:
        item = OrganelleContactSiteProximityItemProfile(
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
    ) -> OrganelleContactSiteProximityMetricTrace:
        trace = OrganelleContactSiteProximityMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[OrganelleContactSiteProximityStudy]:
        result = await self.session.execute(
            select(OrganelleContactSiteProximityStudy)
            .options(
                selectinload(OrganelleContactSiteProximityStudy.item_profiles),
                selectinload(OrganelleContactSiteProximityStudy.metric_traces),
            )
            .where(OrganelleContactSiteProximityStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[OrganelleContactSiteProximityStudy]:
        result = await self.session.execute(
            select(OrganelleContactSiteProximityStudy)
            .options(
                selectinload(OrganelleContactSiteProximityStudy.item_profiles),
                selectinload(OrganelleContactSiteProximityStudy.metric_traces),
            )
            .order_by(OrganelleContactSiteProximityStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
