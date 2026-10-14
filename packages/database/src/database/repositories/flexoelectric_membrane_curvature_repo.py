"""Repository for Phase 473: Autonomous Bio-Piezoelectric Cell Membrane Flexoelectric Curvature Transduction Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.flexoelectric_membrane_curvature import (
    FlexoelectricMembraneCurvatureStudy,
    FlexoelectricMembraneCurvatureItemProfile,
    FlexoelectricMembraneCurvatureMetricTrace,
)


class FlexoelectricMembraneCurvatureRepository:
    """Database operations for Autonomous Bio-Piezoelectric Cell Membrane Flexoelectric Curvature Transduction Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Asymmetric Phospholipid Bilayer Giant Unilamellar Vesicle with Micropipette Aspiration Curvature",
        analytical_modality: str = "flexoelectric-membrane-curvature",
        flexoelectric_coupling_coefficient_pC_per_m: float = 12.4,
        membrane_curvature_radius_nm: float = 45.0,
        transmembrane_induced_polarization_potential_mV: float = 28.5,
        lipid_dipole_reorientation_energy_kj_mol: float = 3.42,
        confidence_score: float = 0.989,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> FlexoelectricMembraneCurvatureStudy:
        study = FlexoelectricMembraneCurvatureStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            flexoelectric_coupling_coefficient_pC_per_m=flexoelectric_coupling_coefficient_pC_per_m,
            membrane_curvature_radius_nm=membrane_curvature_radius_nm,
            transmembrane_induced_polarization_potential_mV=transmembrane_induced_polarization_potential_mV,
            lipid_dipole_reorientation_energy_kj_mol=lipid_dipole_reorientation_energy_kj_mol,
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
    ) -> FlexoelectricMembraneCurvatureItemProfile:
        item = FlexoelectricMembraneCurvatureItemProfile(
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
    ) -> FlexoelectricMembraneCurvatureMetricTrace:
        trace = FlexoelectricMembraneCurvatureMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[FlexoelectricMembraneCurvatureStudy]:
        result = await self.session.execute(
            select(FlexoelectricMembraneCurvatureStudy)
            .options(
                selectinload(FlexoelectricMembraneCurvatureStudy.item_profiles),
                selectinload(FlexoelectricMembraneCurvatureStudy.metric_traces),
            )
            .where(FlexoelectricMembraneCurvatureStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[FlexoelectricMembraneCurvatureStudy]:
        result = await self.session.execute(
            select(FlexoelectricMembraneCurvatureStudy)
            .options(
                selectinload(FlexoelectricMembraneCurvatureStudy.item_profiles),
                selectinload(FlexoelectricMembraneCurvatureStudy.metric_traces),
            )
            .order_by(FlexoelectricMembraneCurvatureStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
