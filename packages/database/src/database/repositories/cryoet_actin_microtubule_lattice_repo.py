"""Repository for Phase 469: Autonomous In-Situ Cryo-ET Cytoskeletal Actin-Microtubule Cross-Linking Structural Lattice Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cryoet_actin_microtubule_lattice import (
    CryoetActinMicrotubuleLatticeStudy,
    CryoetActinMicrotubuleLatticeItemProfile,
    CryoetActinMicrotubuleLatticeMetricTrace,
)


class CryoetActinMicrotubuleLatticeRepository:
    """Database operations for Autonomous In-Situ Cryo-ET Cytoskeletal Actin-Microtubule Cross-Linking Structural Lattice Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Vitrified Primary Growth Cone Cytoskeleton with Septin/Plectin Cross-Linked Filament Assemblies",
        analytical_modality: str = "cryoet-actin-microtubule-lattice",
        crosslinker_bridge_density_per_um: float = 18.5,
        filament_intersection_angle_distribution_deg: float = 48.2,
        subtomogram_correlation_resolution_angstrom: float = 4.85,
        cytoskeletal_network_rigidity_percolation_tau: float = 0.965,
        confidence_score: float = 0.994,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CryoetActinMicrotubuleLatticeStudy:
        study = CryoetActinMicrotubuleLatticeStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            crosslinker_bridge_density_per_um=crosslinker_bridge_density_per_um,
            filament_intersection_angle_distribution_deg=filament_intersection_angle_distribution_deg,
            subtomogram_correlation_resolution_angstrom=subtomogram_correlation_resolution_angstrom,
            cytoskeletal_network_rigidity_percolation_tau=cytoskeletal_network_rigidity_percolation_tau,
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
    ) -> CryoetActinMicrotubuleLatticeItemProfile:
        item = CryoetActinMicrotubuleLatticeItemProfile(
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
    ) -> CryoetActinMicrotubuleLatticeMetricTrace:
        trace = CryoetActinMicrotubuleLatticeMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CryoetActinMicrotubuleLatticeStudy]:
        result = await self.session.execute(
            select(CryoetActinMicrotubuleLatticeStudy)
            .options(
                selectinload(CryoetActinMicrotubuleLatticeStudy.item_profiles),
                selectinload(CryoetActinMicrotubuleLatticeStudy.metric_traces),
            )
            .where(CryoetActinMicrotubuleLatticeStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[CryoetActinMicrotubuleLatticeStudy]:
        result = await self.session.execute(
            select(CryoetActinMicrotubuleLatticeStudy)
            .options(
                selectinload(CryoetActinMicrotubuleLatticeStudy.item_profiles),
                selectinload(CryoetActinMicrotubuleLatticeStudy.metric_traces),
            )
            .order_by(CryoetActinMicrotubuleLatticeStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
