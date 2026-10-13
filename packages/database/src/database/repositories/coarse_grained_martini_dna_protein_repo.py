"""Repository for Phase 447: Autonomous Coarse-Grained DNA-Protein Complex Martini Force-Field Molecular Dynamics Simulator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.coarse_grained_martini_dna_protein import (
    CoarseGrainedMartiniDnaProteinStudy,
    CoarseGrainedMartiniDnaProteinItemProfile,
    CoarseGrainedMartiniDnaProteinMetricTrace,
)


class CoarseGrainedMartiniDnaProteinRepository:
    """Database operations for Autonomous Coarse-Grained DNA-Protein Complex Martini Force-Field Molecular Dynamics Simulator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Nucleosome Core Particle Octamer with 147bp Wrapped DNA in 150mM Salt Solvation Box",
        analytical_modality: str = "coarse-grained-martini-dynamics",
        bead_rmsd_convergence_angstrom: float = 2.15,
        electrostatic_solvation_free_energy_kcal_mol: float = -342.5,
        conformational_sampling_speedup_factor: float = 85.0,
        contact_pair_distribution_g_r: float = 1.48,
        confidence_score: float = 0.993,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CoarseGrainedMartiniDnaProteinStudy:
        study = CoarseGrainedMartiniDnaProteinStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            bead_rmsd_convergence_angstrom=bead_rmsd_convergence_angstrom,
            electrostatic_solvation_free_energy_kcal_mol=electrostatic_solvation_free_energy_kcal_mol,
            conformational_sampling_speedup_factor=conformational_sampling_speedup_factor,
            contact_pair_distribution_g_r=contact_pair_distribution_g_r,
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
    ) -> CoarseGrainedMartiniDnaProteinItemProfile:
        item = CoarseGrainedMartiniDnaProteinItemProfile(
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
    ) -> CoarseGrainedMartiniDnaProteinMetricTrace:
        trace = CoarseGrainedMartiniDnaProteinMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CoarseGrainedMartiniDnaProteinStudy]:
        result = await self.session.execute(
            select(CoarseGrainedMartiniDnaProteinStudy)
            .options(
                selectinload(CoarseGrainedMartiniDnaProteinStudy.item_profiles),
                selectinload(CoarseGrainedMartiniDnaProteinStudy.metric_traces),
            )
            .where(CoarseGrainedMartiniDnaProteinStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[CoarseGrainedMartiniDnaProteinStudy]:
        result = await self.session.execute(
            select(CoarseGrainedMartiniDnaProteinStudy)
            .options(
                selectinload(CoarseGrainedMartiniDnaProteinStudy.item_profiles),
                selectinload(CoarseGrainedMartiniDnaProteinStudy.metric_traces),
            )
            .order_by(CoarseGrainedMartiniDnaProteinStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
