"""Repository for Phase 454: Autonomous Synthetic Cell-Free Compartmentalized Gene Circuit Quorum Feedback Oscillator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cell_free_quorum_feedback_oscillator import (
    CellFreeQuorumFeedbackOscillatorStudy,
    CellFreeQuorumFeedbackOscillatorItemProfile,
    CellFreeQuorumFeedbackOscillatorMetricTrace,
)


class CellFreeQuorumFeedbackOscillatorRepository:
    """Database operations for Autonomous Synthetic Cell-Free Compartmentalized Gene Circuit Quorum Feedback Oscillator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Micro-Emulsion Lipid Vesicles with LuxI/LuxR Synthetic Transcriptional Auto-Inducer Network",
        analytical_modality: str = "cell-free-quorum-oscillator",
        quorum_oscillation_periodicity_hours: float = 3.45,
        ahl_autoinducer_diffusion_flux_umol_cm2_s: float = 0.082,
        inter_compartment_synchronization_index: float = 0.945,
        circuit_persistence_lifetime_hours: float = 42.0,
        confidence_score: float = 0.987,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CellFreeQuorumFeedbackOscillatorStudy:
        study = CellFreeQuorumFeedbackOscillatorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            quorum_oscillation_periodicity_hours=quorum_oscillation_periodicity_hours,
            ahl_autoinducer_diffusion_flux_umol_cm2_s=ahl_autoinducer_diffusion_flux_umol_cm2_s,
            inter_compartment_synchronization_index=inter_compartment_synchronization_index,
            circuit_persistence_lifetime_hours=circuit_persistence_lifetime_hours,
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
    ) -> CellFreeQuorumFeedbackOscillatorItemProfile:
        item = CellFreeQuorumFeedbackOscillatorItemProfile(
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
    ) -> CellFreeQuorumFeedbackOscillatorMetricTrace:
        trace = CellFreeQuorumFeedbackOscillatorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CellFreeQuorumFeedbackOscillatorStudy]:
        result = await self.session.execute(
            select(CellFreeQuorumFeedbackOscillatorStudy)
            .options(
                selectinload(CellFreeQuorumFeedbackOscillatorStudy.item_profiles),
                selectinload(CellFreeQuorumFeedbackOscillatorStudy.metric_traces),
            )
            .where(CellFreeQuorumFeedbackOscillatorStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[CellFreeQuorumFeedbackOscillatorStudy]:
        result = await self.session.execute(
            select(CellFreeQuorumFeedbackOscillatorStudy)
            .options(
                selectinload(CellFreeQuorumFeedbackOscillatorStudy.item_profiles),
                selectinload(CellFreeQuorumFeedbackOscillatorStudy.metric_traces),
            )
            .order_by(CellFreeQuorumFeedbackOscillatorStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
