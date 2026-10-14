"""Repository for Phase 494: Autonomous Mechanosensitive Ion Channel PIEZO1 Gating & Membrane Tension Indentation Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.piezo_mechanosensitive_channel_gating import (
    PiezoMechanosensitiveChannelGatingStudy,
    PiezoMechanosensitiveChannelGatingItemProfile,
    PiezoMechanosensitiveChannelGatingMetricTrace,
)


class PiezoMechanosensitiveChannelGatingRepository:
    """Database operations for Autonomous Mechanosensitive Ion Channel PIEZO1 Gating & Membrane Tension Indentation Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "High-Speed Pressure Clamped HEK293 Cell expressing Human PIEZO1 Trimeric Propeller Blades",
        analytical_modality: str = "piezo-mechanosensitive-gating",
        half_maximal_activation_tension_mN_per_m: float = 2.85,
        channel_open_probability_p_open: float = 0.945,
        single_channel_conductance_pS: float = 29.5,
        mechanical_inactivation_tau_ms: float = 16.2,
        confidence_score: float = 0.994,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> PiezoMechanosensitiveChannelGatingStudy:
        study = PiezoMechanosensitiveChannelGatingStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            half_maximal_activation_tension_mN_per_m=half_maximal_activation_tension_mN_per_m,
            channel_open_probability_p_open=channel_open_probability_p_open,
            single_channel_conductance_pS=single_channel_conductance_pS,
            mechanical_inactivation_tau_ms=mechanical_inactivation_tau_ms,
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
    ) -> PiezoMechanosensitiveChannelGatingItemProfile:
        item = PiezoMechanosensitiveChannelGatingItemProfile(
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
    ) -> PiezoMechanosensitiveChannelGatingMetricTrace:
        trace = PiezoMechanosensitiveChannelGatingMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[PiezoMechanosensitiveChannelGatingStudy]:
        result = await self.session.execute(
            select(PiezoMechanosensitiveChannelGatingStudy)
            .options(
                selectinload(PiezoMechanosensitiveChannelGatingStudy.item_profiles),
                selectinload(PiezoMechanosensitiveChannelGatingStudy.metric_traces),
            )
            .where(PiezoMechanosensitiveChannelGatingStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[PiezoMechanosensitiveChannelGatingStudy]:
        result = await self.session.execute(
            select(PiezoMechanosensitiveChannelGatingStudy)
            .options(
                selectinload(PiezoMechanosensitiveChannelGatingStudy.item_profiles),
                selectinload(PiezoMechanosensitiveChannelGatingStudy.metric_traces),
            )
            .order_by(PiezoMechanosensitiveChannelGatingStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
