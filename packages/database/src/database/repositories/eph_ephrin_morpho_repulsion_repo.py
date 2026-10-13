"""Repository for Phase 468: Autonomous Synthetic Morphogenetic Morpho-Kinetic Boundary Sharpening & Eph-Ephrin Repulsion Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.eph_ephrin_morpho_repulsion import (
    EphEphrinMorphoRepulsionStudy,
    EphEphrinMorphoRepulsionItemProfile,
    EphEphrinMorphoRepulsionMetricTrace,
)


class EphEphrinMorphoRepulsionRepository:
    """Database operations for Autonomous Synthetic Morphogenetic Morpho-Kinetic Boundary Sharpening & Eph-Ephrin Repulsion Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "HEK293T EphB2/EphrinB1 Co-Culture Mosaic Boundary Array in Micropatterned Substrates",
        analytical_modality: str = "eph-ephrin-morpho-repulsion",
        interface_roughness_boundary_width_um: float = 6.8,
        eph_receptor_clustering_density_per_um2: float = 420.0,
        contact_repulsion_retraction_velocity_um_min: float = 2.45,
        heterotypic_sorting_order_parameter: float = 0.945,
        confidence_score: float = 0.99,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> EphEphrinMorphoRepulsionStudy:
        study = EphEphrinMorphoRepulsionStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            interface_roughness_boundary_width_um=interface_roughness_boundary_width_um,
            eph_receptor_clustering_density_per_um2=eph_receptor_clustering_density_per_um2,
            contact_repulsion_retraction_velocity_um_min=contact_repulsion_retraction_velocity_um_min,
            heterotypic_sorting_order_parameter=heterotypic_sorting_order_parameter,
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
    ) -> EphEphrinMorphoRepulsionItemProfile:
        item = EphEphrinMorphoRepulsionItemProfile(
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
    ) -> EphEphrinMorphoRepulsionMetricTrace:
        trace = EphEphrinMorphoRepulsionMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[EphEphrinMorphoRepulsionStudy]:
        result = await self.session.execute(
            select(EphEphrinMorphoRepulsionStudy)
            .options(
                selectinload(EphEphrinMorphoRepulsionStudy.item_profiles),
                selectinload(EphEphrinMorphoRepulsionStudy.metric_traces),
            )
            .where(EphEphrinMorphoRepulsionStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[EphEphrinMorphoRepulsionStudy]:
        result = await self.session.execute(
            select(EphEphrinMorphoRepulsionStudy)
            .options(
                selectinload(EphEphrinMorphoRepulsionStudy.item_profiles),
                selectinload(EphEphrinMorphoRepulsionStudy.metric_traces),
            )
            .order_by(EphEphrinMorphoRepulsionStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
