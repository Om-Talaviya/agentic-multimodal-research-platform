"""Repository for Phase 552: Autonomous Deep Learning De Novo Ribosome Binding Site (RBS) Translation Initiation Rate Optimizer."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.denovo_rbs_translation_initiation_optimizer import (
    DenovoRbsTranslationInitiationOptimizerStudy,
    DenovoRbsTranslationInitiationOptimizerItemProfile,
    DenovoRbsTranslationInitiationOptimizerMetricTrace,
)


class DenovoRbsTranslationInitiationOptimizerRepository:
    """Database operations for Autonomous Deep Learning De Novo Ribosome Binding Site (RBS) Translation Initiation Rate Optimizer."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Synthetic mRNA Polycistronic Operon 5' UTR Shine-Dalgarno Core Library in Escherichia coli BL21(DE3)",
        analytical_modality: str = "de-novo-rbs-optimization",
        translation_initiation_rate_arbitrary_units: float = 48500.0,
        rna_secondary_structure_free_energy_kcal_mol: float = -14.8,
        shine_dalgarno_16s_rrna_hybridization_energy: float = -9.4,
        cross_cistronic_translational_coupling_ratio: float = 0.88,
        confidence_score: float = 0.997,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> DenovoRbsTranslationInitiationOptimizerStudy:
        study = DenovoRbsTranslationInitiationOptimizerStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            translation_initiation_rate_arbitrary_units=translation_initiation_rate_arbitrary_units,
            rna_secondary_structure_free_energy_kcal_mol=rna_secondary_structure_free_energy_kcal_mol,
            shine_dalgarno_16s_rrna_hybridization_energy=shine_dalgarno_16s_rrna_hybridization_energy,
            cross_cistronic_translational_coupling_ratio=cross_cistronic_translational_coupling_ratio,
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
    ) -> DenovoRbsTranslationInitiationOptimizerItemProfile:
        item = DenovoRbsTranslationInitiationOptimizerItemProfile(
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
    ) -> DenovoRbsTranslationInitiationOptimizerMetricTrace:
        trace = DenovoRbsTranslationInitiationOptimizerMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[DenovoRbsTranslationInitiationOptimizerStudy]:
        stmt = (
            select(DenovoRbsTranslationInitiationOptimizerStudy)
            .where(DenovoRbsTranslationInitiationOptimizerStudy.id == study_id)
            .options(
                selectinload(DenovoRbsTranslationInitiationOptimizerStudy.item_profiles),
                selectinload(DenovoRbsTranslationInitiationOptimizerStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[DenovoRbsTranslationInitiationOptimizerStudy]:
        stmt = (
            select(DenovoRbsTranslationInitiationOptimizerStudy)
            .order_by(DenovoRbsTranslationInitiationOptimizerStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(DenovoRbsTranslationInitiationOptimizerStudy.item_profiles),
                selectinload(DenovoRbsTranslationInitiationOptimizerStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
