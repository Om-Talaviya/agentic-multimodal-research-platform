"""Repository for Phase 505: Autonomous In-Cell Single-Molecule FRET Ribosome Conformational Dynamics Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.ribosome_in_cell_conformation_smfret import (
    RibosomeInCellConformationSmfretStudy,
    RibosomeInCellConformationSmfretItemProfile,
    RibosomeInCellConformationSmfretMetricTrace,
)


class RibosomeInCellConformationSmfretRepository:
    """Database operations for Autonomous In-Cell Single-Molecule FRET Ribosome Conformational Dynamics Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Intact Vitrified E. coli Cell with Dual-Fluorophore Cy3/Cy5 L11-Stalk Ribosomal Probes",
        analytical_modality: str = "in-cell-smfret-ribosome",
        intersubunit_rotation_fret_efficiency: float = 0.785,
        translation_elongation_cycle_rate_s_inv: float = 18.2,
        crowding_induced_stalk_fluctuation_std: float = 0.045,
        intact_cell_fluorophore_photobleaching_lifetime_s: float = 42.0,
        confidence_score: float = 0.994,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> RibosomeInCellConformationSmfretStudy:
        study = RibosomeInCellConformationSmfretStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            intersubunit_rotation_fret_efficiency=intersubunit_rotation_fret_efficiency,
            translation_elongation_cycle_rate_s_inv=translation_elongation_cycle_rate_s_inv,
            crowding_induced_stalk_fluctuation_std=crowding_induced_stalk_fluctuation_std,
            intact_cell_fluorophore_photobleaching_lifetime_s=intact_cell_fluorophore_photobleaching_lifetime_s,
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
    ) -> RibosomeInCellConformationSmfretItemProfile:
        item = RibosomeInCellConformationSmfretItemProfile(
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
    ) -> RibosomeInCellConformationSmfretMetricTrace:
        trace = RibosomeInCellConformationSmfretMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[RibosomeInCellConformationSmfretStudy]:
        result = await self.session.execute(
            select(RibosomeInCellConformationSmfretStudy)
            .options(
                selectinload(RibosomeInCellConformationSmfretStudy.item_profiles),
                selectinload(RibosomeInCellConformationSmfretStudy.metric_traces),
            )
            .where(RibosomeInCellConformationSmfretStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[RibosomeInCellConformationSmfretStudy]:
        result = await self.session.execute(
            select(RibosomeInCellConformationSmfretStudy)
            .options(
                selectinload(RibosomeInCellConformationSmfretStudy.item_profiles),
                selectinload(RibosomeInCellConformationSmfretStudy.metric_traces),
            )
            .order_by(RibosomeInCellConformationSmfretStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
