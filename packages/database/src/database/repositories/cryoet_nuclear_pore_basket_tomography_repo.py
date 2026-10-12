"""Repository for Phase 438: Autonomous Cryo-ET In-Situ Nuclear Pore Complex (NPC) Nuclear Basket Dynamic Conformation Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cryoet_nuclear_pore_basket_tomography import (
    CryoetNuclearPoreBasketStudy,
    CryoetNuclearPoreBasketItemProfile,
    CryoetNuclearPoreBasketMetricTrace,
)


class CryoetNuclearPoreBasketRepository:
    """Database operations for Autonomous Cryo-ET In-Situ Nuclear Pore Complex (NPC) Nuclear Basket Dynamic Conformation Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Intact HeLa Cell Nuclear Envelope Vitreous Lamella with 8-Fold NPC Basket",
        analytical_modality: str = "cryoet-npc-basket",
        subtomogram_average_resolution_angstrom: float = 4.15,
        basket_dilation_radius_nm: float = 26.8,
        fg_nucleoporin_confinement_entropy: float = -14.2,
        transport_receptor_docking_occupancy: float = 0.924,
        confidence_score: float = 0.99,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CryoetNuclearPoreBasketStudy:
        study = CryoetNuclearPoreBasketStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            subtomogram_average_resolution_angstrom=subtomogram_average_resolution_angstrom,
            basket_dilation_radius_nm=basket_dilation_radius_nm,
            fg_nucleoporin_confinement_entropy=fg_nucleoporin_confinement_entropy,
            transport_receptor_docking_occupancy=transport_receptor_docking_occupancy,
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
    ) -> CryoetNuclearPoreBasketItemProfile:
        item = CryoetNuclearPoreBasketItemProfile(
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
    ) -> CryoetNuclearPoreBasketMetricTrace:
        trace = CryoetNuclearPoreBasketMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CryoetNuclearPoreBasketStudy]:
        result = await self.session.execute(
            select(CryoetNuclearPoreBasketStudy)
            .options(
                selectinload(CryoetNuclearPoreBasketStudy.item_profiles),
                selectinload(CryoetNuclearPoreBasketStudy.metric_traces),
            )
            .where(CryoetNuclearPoreBasketStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[CryoetNuclearPoreBasketStudy]:
        result = await self.session.execute(
            select(CryoetNuclearPoreBasketStudy)
            .options(
                selectinload(CryoetNuclearPoreBasketStudy.item_profiles),
                selectinload(CryoetNuclearPoreBasketStudy.metric_traces),
            )
            .order_by(CryoetNuclearPoreBasketStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
