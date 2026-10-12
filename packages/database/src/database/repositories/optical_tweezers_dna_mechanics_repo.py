"""Repository for Phase 416: Autonomous Optical Tweezers DNA-Protein Mechanical Tension & Force-Extension Overstretching Modeler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.optical_tweezers_dna_mechanics import (
    OpticalTweezersDnaMechanicsStudy,
    OpticalTweezersDnaMechanicsItemProfile,
    OpticalTweezersDnaMechanicsMetricTrace,
)


class OpticalTweezersDnaMechanicsRepository:
    """Database operations for Autonomous Optical Tweezers DNA-Protein Mechanical Tension & Force-Extension Overstretching Modeler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Single-Molecule Lambda-DNA Tether with RecA Nucleoprotein",
        analytical_modality: str = "optical-tweezers",
        overstretching_transition_force_pN: float = 65.4,
        persistence_length_nm: float = 47.8,
        contour_length_um: float = 16.2,
        trap_stiffness_pN_per_nm: float = 0.185,
        confidence_score: float = 0.991,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> OpticalTweezersDnaMechanicsStudy:
        study = OpticalTweezersDnaMechanicsStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            overstretching_transition_force_pN=overstretching_transition_force_pN,
            persistence_length_nm=persistence_length_nm,
            contour_length_um=contour_length_um,
            trap_stiffness_pN_per_nm=trap_stiffness_pN_per_nm,
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
    ) -> OpticalTweezersDnaMechanicsItemProfile:
        item = OpticalTweezersDnaMechanicsItemProfile(
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
    ) -> OpticalTweezersDnaMechanicsMetricTrace:
        trace = OpticalTweezersDnaMechanicsMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[OpticalTweezersDnaMechanicsStudy]:
        result = await self.session.execute(
            select(OpticalTweezersDnaMechanicsStudy)
            .options(
                selectinload(OpticalTweezersDnaMechanicsStudy.item_profiles),
                selectinload(OpticalTweezersDnaMechanicsStudy.metric_traces),
            )
            .where(OpticalTweezersDnaMechanicsStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[OpticalTweezersDnaMechanicsStudy]:
        result = await self.session.execute(
            select(OpticalTweezersDnaMechanicsStudy)
            .options(
                selectinload(OpticalTweezersDnaMechanicsStudy.item_profiles),
                selectinload(OpticalTweezersDnaMechanicsStudy.metric_traces),
            )
            .order_by(OpticalTweezersDnaMechanicsStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
