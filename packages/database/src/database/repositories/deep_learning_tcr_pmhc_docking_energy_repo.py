"""Repository for Phase 514: Autonomous Equivariant Graph Neural Network TCR-pMHC Interface Binding Energy Forecaster."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.deep_learning_tcr_pmhc_docking_energy import (
    DeepLearningTcrPmhcDockingEnergyStudy,
    DeepLearningTcrPmhcDockingEnergyItemProfile,
    DeepLearningTcrPmhcDockingEnergyMetricTrace,
)


class DeepLearningTcrPmhcDockingEnergyRepository:
    """Database operations for Autonomous Equivariant Graph Neural Network TCR-pMHC Interface Binding Energy Forecaster."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Structure-Resolved Complex of Human CD8+ TCR with Cancer-Testis Neoantigen NY-ESO-1 HLA-A*02:01",
        analytical_modality: str = "egnn-tcr-pmhc-docking",
        predicted_binding_free_energy_delta_G_kcal_mol: float = -10.45,
        cdr3_loop_interface_contact_rmsd_angstrom: float = 0.85,
        allotype_cross_reactivity_prediction_auroc: float = 0.965,
        dissociation_constant_kd_nM: float = 45.0,
        confidence_score: float = 0.995,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> DeepLearningTcrPmhcDockingEnergyStudy:
        study = DeepLearningTcrPmhcDockingEnergyStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            predicted_binding_free_energy_delta_G_kcal_mol=predicted_binding_free_energy_delta_G_kcal_mol,
            cdr3_loop_interface_contact_rmsd_angstrom=cdr3_loop_interface_contact_rmsd_angstrom,
            allotype_cross_reactivity_prediction_auroc=allotype_cross_reactivity_prediction_auroc,
            dissociation_constant_kd_nM=dissociation_constant_kd_nM,
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
    ) -> DeepLearningTcrPmhcDockingEnergyItemProfile:
        item = DeepLearningTcrPmhcDockingEnergyItemProfile(
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
    ) -> DeepLearningTcrPmhcDockingEnergyMetricTrace:
        trace = DeepLearningTcrPmhcDockingEnergyMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[DeepLearningTcrPmhcDockingEnergyStudy]:
        result = await self.session.execute(
            select(DeepLearningTcrPmhcDockingEnergyStudy)
            .options(
                selectinload(DeepLearningTcrPmhcDockingEnergyStudy.item_profiles),
                selectinload(DeepLearningTcrPmhcDockingEnergyStudy.metric_traces),
            )
            .where(DeepLearningTcrPmhcDockingEnergyStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DeepLearningTcrPmhcDockingEnergyStudy]:
        result = await self.session.execute(
            select(DeepLearningTcrPmhcDockingEnergyStudy)
            .options(
                selectinload(DeepLearningTcrPmhcDockingEnergyStudy.item_profiles),
                selectinload(DeepLearningTcrPmhcDockingEnergyStudy.metric_traces),
            )
            .order_by(DeepLearningTcrPmhcDockingEnergyStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
