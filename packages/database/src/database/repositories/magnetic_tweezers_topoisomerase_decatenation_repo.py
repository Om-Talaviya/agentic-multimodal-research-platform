"""Repository for Phase 484: Autonomous Single-Molecule Magnetic Tweezers Topoisomerase Type II DNA Catenation Decatenator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.magnetic_tweezers_topoisomerase_decatenation import (
    MagneticTweezersTopoisomeraseDecatenationStudy,
    MagneticTweezersTopoisomeraseDecatenationItemProfile,
    MagneticTweezersTopoisomeraseDecatenationMetricTrace,
)


class MagneticTweezersTopoisomeraseDecatenationRepository:
    """Database operations for Autonomous Single-Molecule Magnetic Tweezers Topoisomerase Type II DNA Catenation Decatenator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Tethered Braided DNA Minicircle Pair with Purified Human Topoisomerase II-alpha in Flow Cell",
        analytical_modality: str = "magnetic-tweezers-decatenation",
        decatenation_catalytic_rate_per_sec: float = 3.85,
        atp_hydrolysis_coupling_ratio: float = 1.98,
        t_segment_strand_passage_dwell_time_ms: float = 145.0,
        supercoiling_linking_number_delta: float = -2.0,
        confidence_score: float = 0.992,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MagneticTweezersTopoisomeraseDecatenationStudy:
        study = MagneticTweezersTopoisomeraseDecatenationStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            decatenation_catalytic_rate_per_sec=decatenation_catalytic_rate_per_sec,
            atp_hydrolysis_coupling_ratio=atp_hydrolysis_coupling_ratio,
            t_segment_strand_passage_dwell_time_ms=t_segment_strand_passage_dwell_time_ms,
            supercoiling_linking_number_delta=supercoiling_linking_number_delta,
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
    ) -> MagneticTweezersTopoisomeraseDecatenationItemProfile:
        item = MagneticTweezersTopoisomeraseDecatenationItemProfile(
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
    ) -> MagneticTweezersTopoisomeraseDecatenationMetricTrace:
        trace = MagneticTweezersTopoisomeraseDecatenationMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MagneticTweezersTopoisomeraseDecatenationStudy]:
        result = await self.session.execute(
            select(MagneticTweezersTopoisomeraseDecatenationStudy)
            .options(
                selectinload(MagneticTweezersTopoisomeraseDecatenationStudy.item_profiles),
                selectinload(MagneticTweezersTopoisomeraseDecatenationStudy.metric_traces),
            )
            .where(MagneticTweezersTopoisomeraseDecatenationStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[MagneticTweezersTopoisomeraseDecatenationStudy]:
        result = await self.session.execute(
            select(MagneticTweezersTopoisomeraseDecatenationStudy)
            .options(
                selectinload(MagneticTweezersTopoisomeraseDecatenationStudy.item_profiles),
                selectinload(MagneticTweezersTopoisomeraseDecatenationStudy.metric_traces),
            )
            .order_by(MagneticTweezersTopoisomeraseDecatenationStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
