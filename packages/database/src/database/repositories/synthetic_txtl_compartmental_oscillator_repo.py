"""Repository for Phase 488: Autonomous Cell-Free Compartmentalized Synthetic Transcription-Translation (TX-TL) Feedback Oscillator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.synthetic_txtl_compartmental_oscillator import (
    SyntheticTxtlCompartmentalOscillatorStudy,
    SyntheticTxtlCompartmentalOscillatorItemProfile,
    SyntheticTxtlCompartmentalOscillatorMetricTrace,
)


class SyntheticTxtlCompartmentalOscillatorRepository:
    """Database operations for Autonomous Cell-Free Compartmentalized Synthetic Transcription-Translation (TX-TL) Feedback Oscillator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Continuous Microfluidic Droplet-Exchanged E. coli Cell-Free Expression Matrix with Repressilator Circuit",
        analytical_modality: str = "txtl-compartmental-oscillator",
        oscillation_periodicity_hours: float = 3.4,
        peak_to_trough_amplitude_fold_change: float = 18.5,
        atp_regeneration_flux_mM_per_hr: float = 1.8,
        oscillation_undamped_cycle_count: float = 24.0,
        confidence_score: float = 0.99,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SyntheticTxtlCompartmentalOscillatorStudy:
        study = SyntheticTxtlCompartmentalOscillatorStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            oscillation_periodicity_hours=oscillation_periodicity_hours,
            peak_to_trough_amplitude_fold_change=peak_to_trough_amplitude_fold_change,
            atp_regeneration_flux_mM_per_hr=atp_regeneration_flux_mM_per_hr,
            oscillation_undamped_cycle_count=oscillation_undamped_cycle_count,
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
    ) -> SyntheticTxtlCompartmentalOscillatorItemProfile:
        item = SyntheticTxtlCompartmentalOscillatorItemProfile(
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
    ) -> SyntheticTxtlCompartmentalOscillatorMetricTrace:
        trace = SyntheticTxtlCompartmentalOscillatorMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SyntheticTxtlCompartmentalOscillatorStudy]:
        result = await self.session.execute(
            select(SyntheticTxtlCompartmentalOscillatorStudy)
            .options(
                selectinload(SyntheticTxtlCompartmentalOscillatorStudy.item_profiles),
                selectinload(SyntheticTxtlCompartmentalOscillatorStudy.metric_traces),
            )
            .where(SyntheticTxtlCompartmentalOscillatorStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[SyntheticTxtlCompartmentalOscillatorStudy]:
        result = await self.session.execute(
            select(SyntheticTxtlCompartmentalOscillatorStudy)
            .options(
                selectinload(SyntheticTxtlCompartmentalOscillatorStudy.item_profiles),
                selectinload(SyntheticTxtlCompartmentalOscillatorStudy.metric_traces),
            )
            .order_by(SyntheticTxtlCompartmentalOscillatorStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
