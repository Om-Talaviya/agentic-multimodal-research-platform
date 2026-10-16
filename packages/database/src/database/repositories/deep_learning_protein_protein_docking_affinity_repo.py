"""Repository for Phase 573: Autonomous Equivariant SE(3) Diffusion Deep Learning Protein-Protein Interaction (PPI) Complex Docking & Binding Affinity Forecaster."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.deep_learning_protein_protein_docking_affinity import (
    DeepLearningProteinProteinDockingAffinityStudy,
    DeepLearningProteinProteinDockingAffinityItemProfile,
    DeepLearningProteinProteinDockingAffinityMetricTrace,
)


class DeepLearningProteinProteinDockingAffinityRepository:
    """Repository for Autonomous Equivariant SE(3) Diffusion Deep Learning Protein-Protein Interaction (PPI) Complex Docking & Binding Affinity Forecaster storage and retrieval."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str,
        analytical_modality: str,
        interface_rmsd_angstrom: float,
        binding_free_energy_delta_g_kcal_mol: float,
        docking_pose_confidence_plddt: float,
        buried_surface_area_angstrom2: float,
        confidence_score: float = 0.998,
        status: str = "completed",
        summary_report: Optional[str] = None,
        parameters: Optional[dict] = None,
    ) -> DeepLearningProteinProteinDockingAffinityStudy:
        study = DeepLearningProteinProteinDockingAffinityStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            interface_rmsd_angstrom=interface_rmsd_angstrom,
            binding_free_energy_delta_g_kcal_mol=binding_free_energy_delta_g_kcal_mol,
            docking_pose_confidence_plddt=docking_pose_confidence_plddt,
            buried_surface_area_angstrom2=buried_surface_area_angstrom2,
            confidence_score=confidence_score,
            status=status,
            summary_report=summary_report,
            parameters=parameters or {},
        )
        self.session.add(study)
        await self.session.commit()
        await self.session.refresh(study)
        return study

    async def get_study(self, study_id: UUID) -> Optional[DeepLearningProteinProteinDockingAffinityStudy]:
        stmt = select(DeepLearningProteinProteinDockingAffinityStudy).where(DeepLearningProteinProteinDockingAffinityStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[DeepLearningProteinProteinDockingAffinityStudy]:
        stmt = select(DeepLearningProteinProteinDockingAffinityStudy).order_by(DeepLearningProteinProteinDockingAffinityStudy.created_at.desc()).limit(limit)
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
    ) -> DeepLearningProteinProteinDockingAffinityItemProfile:
        profile = DeepLearningProteinProteinDockingAffinityItemProfile(
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
    ) -> DeepLearningProteinProteinDockingAffinityMetricTrace:
        trace = DeepLearningProteinProteinDockingAffinityMetricTrace(
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
