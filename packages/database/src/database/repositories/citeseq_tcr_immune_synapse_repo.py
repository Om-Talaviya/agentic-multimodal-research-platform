"""Repository for Phase 420: Autonomous Single-Cell Multi-Modal CITE-seq & TCR Clonotype Immune Synapse Dynamics Deconvolver."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.citeseq_tcr_immune_synapse import (
    CiteseqTcrImmuneSynapseStudy,
    CiteseqTcrImmuneSynapseItemProfile,
    CiteseqTcrImmuneSynapseMetricTrace,
)


class CiteseqTcrImmuneSynapseRepository:
    """Database operations for Autonomous Single-Cell Multi-Modal CITE-seq & TCR Clonotype Immune Synapse Dynamics Deconvolver."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Human CD8+ Tumor-Infiltrating Lymphocytes with pMHC Multimer",
        analytical_modality: str = "citeseq-tcr-synapse",
        immune_synapse_contact_area_um2: float = 42.6,
        surface_protein_abundance_umi: float = 1420.0,
        tcr_clonotype_affinity_score: float = 0.962,
        cytotoxic_granule_polarization_ratio: float = 0.895,
        confidence_score: float = 0.988,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CiteseqTcrImmuneSynapseStudy:
        study = CiteseqTcrImmuneSynapseStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            immune_synapse_contact_area_um2=immune_synapse_contact_area_um2,
            surface_protein_abundance_umi=surface_protein_abundance_umi,
            tcr_clonotype_affinity_score=tcr_clonotype_affinity_score,
            cytotoxic_granule_polarization_ratio=cytotoxic_granule_polarization_ratio,
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
    ) -> CiteseqTcrImmuneSynapseItemProfile:
        item = CiteseqTcrImmuneSynapseItemProfile(
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
    ) -> CiteseqTcrImmuneSynapseMetricTrace:
        trace = CiteseqTcrImmuneSynapseMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CiteseqTcrImmuneSynapseStudy]:
        result = await self.session.execute(
            select(CiteseqTcrImmuneSynapseStudy)
            .options(
                selectinload(CiteseqTcrImmuneSynapseStudy.item_profiles),
                selectinload(CiteseqTcrImmuneSynapseStudy.metric_traces),
            )
            .where(CiteseqTcrImmuneSynapseStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[CiteseqTcrImmuneSynapseStudy]:
        result = await self.session.execute(
            select(CiteseqTcrImmuneSynapseStudy)
            .options(
                selectinload(CiteseqTcrImmuneSynapseStudy.item_profiles),
                selectinload(CiteseqTcrImmuneSynapseStudy.metric_traces),
            )
            .order_by(CiteseqTcrImmuneSynapseStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
