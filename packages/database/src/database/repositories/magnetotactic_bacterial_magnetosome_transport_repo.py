"""Repository for Phase 551: Autonomous Engineered Magnetotactic Bacterial Magnetosome Nanowire Steering & Drug Cargo Transport Simulator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.magnetotactic_bacterial_magnetosome_transport import (
    MagnetotacticBacterialMagnetosomeTransportStudy,
    MagnetotacticBacterialMagnetosomeTransportItemProfile,
    MagnetotacticBacterialMagnetosomeTransportMetricTrace,
)


class MagnetotacticBacterialMagnetosomeTransportRepository:
    """Database operations for Autonomous Engineered Magnetotactic Bacterial Magnetosome Nanowire Steering & Drug Cargo Transport Simulator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Engineered Magnetospirillum magneticum AMB-1 expressing Doxorubicin-Loaded Membrane Nanovesicles in Microfluidic Vascular Capillaries",
        analytical_modality: str = "bacterial-magnetosome-transport",
        magnetic_steering_velocity_um_s: float = 48.5,
        magnetosome_chain_magnetic_moment_femu: float = 12.5,
        tumor_microvascular_extravasation_rate_pct: float = 34.2,
        nanocarrier_drug_payload_delivery_ng_ml: float = 82.0,
        confidence_score: float = 0.995,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MagnetotacticBacterialMagnetosomeTransportStudy:
        study = MagnetotacticBacterialMagnetosomeTransportStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            magnetic_steering_velocity_um_s=magnetic_steering_velocity_um_s,
            magnetosome_chain_magnetic_moment_femu=magnetosome_chain_magnetic_moment_femu,
            tumor_microvascular_extravasation_rate_pct=tumor_microvascular_extravasation_rate_pct,
            nanocarrier_drug_payload_delivery_ng_ml=nanocarrier_drug_payload_delivery_ng_ml,
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
    ) -> MagnetotacticBacterialMagnetosomeTransportItemProfile:
        item = MagnetotacticBacterialMagnetosomeTransportItemProfile(
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
    ) -> MagnetotacticBacterialMagnetosomeTransportMetricTrace:
        trace = MagnetotacticBacterialMagnetosomeTransportMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MagnetotacticBacterialMagnetosomeTransportStudy]:
        stmt = (
            select(MagnetotacticBacterialMagnetosomeTransportStudy)
            .where(MagnetotacticBacterialMagnetosomeTransportStudy.id == study_id)
            .options(
                selectinload(MagnetotacticBacterialMagnetosomeTransportStudy.item_profiles),
                selectinload(MagnetotacticBacterialMagnetosomeTransportStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[MagnetotacticBacterialMagnetosomeTransportStudy]:
        stmt = (
            select(MagnetotacticBacterialMagnetosomeTransportStudy)
            .order_by(MagnetotacticBacterialMagnetosomeTransportStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(MagnetotacticBacterialMagnetosomeTransportStudy.item_profiles),
                selectinload(MagnetotacticBacterialMagnetosomeTransportStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
