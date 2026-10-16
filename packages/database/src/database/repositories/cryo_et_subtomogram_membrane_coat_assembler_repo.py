"""Repository for Phase 575: Autonomous In-Situ Cryo-ET Subtomogram Averaging Clathrin & COP-II Vesicular Membrane Coat Symmetry Assembler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cryo_et_subtomogram_membrane_coat_assembler import (
    CryoEtSubtomogramMembraneCoatAssemblerStudy,
    CryoEtSubtomogramMembraneCoatAssemblerItemProfile,
    CryoEtSubtomogramMembraneCoatAssemblerMetricTrace,
)


class CryoEtSubtomogramMembraneCoatAssemblerRepository:
    """Repository for Autonomous In-Situ Cryo-ET Subtomogram Averaging Clathrin & COP-II Vesicular Membrane Coat Symmetry Assembler storage and retrieval."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str,
        analytical_modality: str,
        subtomogram_resolution_fsc0143_a: float,
        cage_polyhedral_symmetry_index: float,
        membrane_curvature_coupling_energy_kbt: float,
        angular_orientation_precision_deg: float,
        confidence_score: float = 0.995,
        status: str = "completed",
        summary_report: Optional[str] = None,
        parameters: Optional[dict] = None,
    ) -> CryoEtSubtomogramMembraneCoatAssemblerStudy:
        study = CryoEtSubtomogramMembraneCoatAssemblerStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            subtomogram_resolution_fsc0143_a=subtomogram_resolution_fsc0143_a,
            cage_polyhedral_symmetry_index=cage_polyhedral_symmetry_index,
            membrane_curvature_coupling_energy_kbt=membrane_curvature_coupling_energy_kbt,
            angular_orientation_precision_deg=angular_orientation_precision_deg,
            confidence_score=confidence_score,
            status=status,
            summary_report=summary_report,
            parameters=parameters or {},
        )
        self.session.add(study)
        await self.session.commit()
        await self.session.refresh(study)
        return study

    async def get_study(self, study_id: UUID) -> Optional[CryoEtSubtomogramMembraneCoatAssemblerStudy]:
        stmt = select(CryoEtSubtomogramMembraneCoatAssemblerStudy).where(CryoEtSubtomogramMembraneCoatAssemblerStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[CryoEtSubtomogramMembraneCoatAssemblerStudy]:
        stmt = select(CryoEtSubtomogramMembraneCoatAssemblerStudy).order_by(CryoEtSubtomogramMembraneCoatAssemblerStudy.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_item_profile(
        self,
        study_id: UUID,
        item_name: str,
        quantitative_value: float,
        profile_category: str = "Analysis Profile",
        log2_fold_change: float = 1.5,
        significance_score: float = 0.95,
    ) -> CryoEtSubtomogramMembraneCoatAssemblerItemProfile:
        profile = CryoEtSubtomogramMembraneCoatAssemblerItemProfile(
            study_id=study_id,
            item_name=item_name,
            profile_category=profile_category,
            quantitative_value=quantitative_value,
            log2_fold_change=log2_fold_change,
            significance_score=significance_score,
        )
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def add_metric_trace(
        self,
        study_id: UUID,
        metric_dimension: str,
        observed_value: float,
        z_score: float = 0.0,
        p_value: float = 0.05,
    ) -> CryoEtSubtomogramMembraneCoatAssemblerMetricTrace:
        trace = CryoEtSubtomogramMembraneCoatAssemblerMetricTrace(
            study_id=study_id,
            metric_dimension=metric_dimension,
            observed_value=observed_value,
            z_score=z_score,
            p_value=p_value,
        )
        self.session.add(trace)
        await self.session.commit()
        await self.session.refresh(trace)
        return trace
