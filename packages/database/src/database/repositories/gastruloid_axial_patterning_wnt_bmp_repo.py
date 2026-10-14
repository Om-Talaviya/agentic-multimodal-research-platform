"""Repository for Phase 496: Autonomous Synthetic Organogenesis Gastruloid Axial Patterning & Wnt-BMP Morphogenetic Polarization Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.gastruloid_axial_patterning_wnt_bmp import (
    GastruloidAxialPatterningWntBmpStudy,
    GastruloidAxialPatterningWntBmpItemProfile,
    GastruloidAxialPatterningWntBmpMetricTrace,
)


class GastruloidAxialPatterningWntBmpRepository:
    """Database operations for Autonomous Synthetic Organogenesis Gastruloid Axial Patterning & Wnt-BMP Morphogenetic Polarization Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "3D Aggregated Human Embryonic Stem Cell Gastruloids under Chir99021 Pulse Induction",
        analytical_modality: str = "gastruloid-axial-patterning",
        anteroposterior_elongation_aspect_ratio: float = 3.65,
        bra_t_posterior_polarization_fraction: float = 0.925,
        somite_like_segmentation_stripe_count: float = 8.0,
        morphogenetic_symmetry_breaking_time_hours: float = 48.0,
        confidence_score: float = 0.995,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> GastruloidAxialPatterningWntBmpStudy:
        study = GastruloidAxialPatterningWntBmpStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            anteroposterior_elongation_aspect_ratio=anteroposterior_elongation_aspect_ratio,
            bra_t_posterior_polarization_fraction=bra_t_posterior_polarization_fraction,
            somite_like_segmentation_stripe_count=somite_like_segmentation_stripe_count,
            morphogenetic_symmetry_breaking_time_hours=morphogenetic_symmetry_breaking_time_hours,
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
    ) -> GastruloidAxialPatterningWntBmpItemProfile:
        item = GastruloidAxialPatterningWntBmpItemProfile(
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
    ) -> GastruloidAxialPatterningWntBmpMetricTrace:
        trace = GastruloidAxialPatterningWntBmpMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[GastruloidAxialPatterningWntBmpStudy]:
        result = await self.session.execute(
            select(GastruloidAxialPatterningWntBmpStudy)
            .options(
                selectinload(GastruloidAxialPatterningWntBmpStudy.item_profiles),
                selectinload(GastruloidAxialPatterningWntBmpStudy.metric_traces),
            )
            .where(GastruloidAxialPatterningWntBmpStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[GastruloidAxialPatterningWntBmpStudy]:
        result = await self.session.execute(
            select(GastruloidAxialPatterningWntBmpStudy)
            .options(
                selectinload(GastruloidAxialPatterningWntBmpStudy.item_profiles),
                selectinload(GastruloidAxialPatterningWntBmpStudy.metric_traces),
            )
            .order_by(GastruloidAxialPatterningWntBmpStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
