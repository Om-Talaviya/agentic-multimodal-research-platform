"""Repository for Phase 572: Autonomous Optogenetic G-Protein-Coupled Receptor (Opto-GPCR) Spatiotemporal Second Messenger Signaling Predictor."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.optogenetic_neuromodulatory_gpc_receptor_activator import (
    OptogeneticNeuromodulatoryGpcReceptorActivatorStudy,
    OptogeneticNeuromodulatoryGpcReceptorActivatorItemProfile,
    OptogeneticNeuromodulatoryGpcReceptorActivatorMetricTrace,
)


class OptogeneticNeuromodulatoryGpcReceptorActivatorRepository:
    """Repository for Autonomous Optogenetic G-Protein-Coupled Receptor (Opto-GPCR) Spatiotemporal Second Messenger Signaling Predictor storage and retrieval."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str,
        analytical_modality: str,
        camp_generation_rate_nm_s: float,
        g_protein_coupling_selectivity: float,
        photocurrent_deactivation_tau_ms: float,
        downstream_phosphorylation_index: float,
        confidence_score: float = 0.995,
        status: str = "completed",
        summary_report: Optional[str] = None,
        parameters: Optional[dict] = None,
    ) -> OptogeneticNeuromodulatoryGpcReceptorActivatorStudy:
        study = OptogeneticNeuromodulatoryGpcReceptorActivatorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            camp_generation_rate_nm_s=camp_generation_rate_nm_s,
            g_protein_coupling_selectivity=g_protein_coupling_selectivity,
            photocurrent_deactivation_tau_ms=photocurrent_deactivation_tau_ms,
            downstream_phosphorylation_index=downstream_phosphorylation_index,
            confidence_score=confidence_score,
            status=status,
            summary_report=summary_report,
            parameters=parameters or {},
        )
        self.session.add(study)
        await self.session.commit()
        await self.session.refresh(study)
        return study

    async def get_study(self, study_id: UUID) -> Optional[OptogeneticNeuromodulatoryGpcReceptorActivatorStudy]:
        stmt = select(OptogeneticNeuromodulatoryGpcReceptorActivatorStudy).where(OptogeneticNeuromodulatoryGpcReceptorActivatorStudy.id == study_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50) -> List[OptogeneticNeuromodulatoryGpcReceptorActivatorStudy]:
        stmt = select(OptogeneticNeuromodulatoryGpcReceptorActivatorStudy).order_by(OptogeneticNeuromodulatoryGpcReceptorActivatorStudy.created_at.desc()).limit(limit)
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
    ) -> OptogeneticNeuromodulatoryGpcReceptorActivatorItemProfile:
        profile = OptogeneticNeuromodulatoryGpcReceptorActivatorItemProfile(
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
    ) -> OptogeneticNeuromodulatoryGpcReceptorActivatorMetricTrace:
        trace = OptogeneticNeuromodulatoryGpcReceptorActivatorMetricTrace(
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
