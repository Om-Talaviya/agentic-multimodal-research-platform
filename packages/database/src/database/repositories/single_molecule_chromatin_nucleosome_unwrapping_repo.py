"""Repository for Phase 558: Autonomous Single-Molecule Mechanical Force Spectroscopy Chromatin Fiber Nucleosome Unwrapping Modeler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.single_molecule_chromatin_nucleosome_unwrapping import (
    SingleMoleculeChromatinNucleosomeUnwrappingStudy,
    SingleMoleculeChromatinNucleosomeUnwrappingItemProfile,
    SingleMoleculeChromatinNucleosomeUnwrappingMetricTrace,
)


class SingleMoleculeChromatinNucleosomeUnwrappingRepository:
    """Database operations for Autonomous Single-Molecule Mechanical Force Spectroscopy Chromatin Fiber Nucleosome Unwrapping Modeler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Reconstituted 12-Nucleosome Chromatin Array with Widom 601 positioning sequences stretched via Dual-Beam Optical Tweezers",
        analytical_modality: str = "chromatin-force-spectroscopy",
        outer_turn_unwrapping_force_threshold_pn: float = 3.8,
        inner_turn_cooperative_rupture_force_pn: float = 15.2,
        histone_octamer_dissociation_work_kcal_mol: float = 26.4,
        unwrapped_dna_contour_length_release_nm: float = 52.0,
        confidence_score: float = 0.996,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SingleMoleculeChromatinNucleosomeUnwrappingStudy:
        study = SingleMoleculeChromatinNucleosomeUnwrappingStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            outer_turn_unwrapping_force_threshold_pn=outer_turn_unwrapping_force_threshold_pn,
            inner_turn_cooperative_rupture_force_pn=inner_turn_cooperative_rupture_force_pn,
            histone_octamer_dissociation_work_kcal_mol=histone_octamer_dissociation_work_kcal_mol,
            unwrapped_dna_contour_length_release_nm=unwrapped_dna_contour_length_release_nm,
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
    ) -> SingleMoleculeChromatinNucleosomeUnwrappingItemProfile:
        item = SingleMoleculeChromatinNucleosomeUnwrappingItemProfile(
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
    ) -> SingleMoleculeChromatinNucleosomeUnwrappingMetricTrace:
        trace = SingleMoleculeChromatinNucleosomeUnwrappingMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SingleMoleculeChromatinNucleosomeUnwrappingStudy]:
        stmt = (
            select(SingleMoleculeChromatinNucleosomeUnwrappingStudy)
            .where(SingleMoleculeChromatinNucleosomeUnwrappingStudy.id == study_id)
            .options(
                selectinload(SingleMoleculeChromatinNucleosomeUnwrappingStudy.item_profiles),
                selectinload(SingleMoleculeChromatinNucleosomeUnwrappingStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[SingleMoleculeChromatinNucleosomeUnwrappingStudy]:
        stmt = (
            select(SingleMoleculeChromatinNucleosomeUnwrappingStudy)
            .order_by(SingleMoleculeChromatinNucleosomeUnwrappingStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(SingleMoleculeChromatinNucleosomeUnwrappingStudy.item_profiles),
                selectinload(SingleMoleculeChromatinNucleosomeUnwrappingStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
