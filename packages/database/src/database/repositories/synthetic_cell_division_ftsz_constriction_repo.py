"""Repository for Phase 541: Autonomous Synthetic Protocellular Compartment FtsZ-Min System Dynamic Cleavage Constriction Modeler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.synthetic_cell_division_ftsz_constriction import (
    SyntheticCellDivisionFtszConstrictionStudy,
    SyntheticCellDivisionFtszConstrictionItemProfile,
    SyntheticCellDivisionFtszConstrictionMetricTrace,
)


class SyntheticCellDivisionFtszConstrictionRepository:
    """Database operations for Autonomous Synthetic Protocellular Compartment FtsZ-Min System Dynamic Cleavage Constriction Modeler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Cell-Free Microfluidic Giant Unilamellar Vesicle with Reconstituted FtsZ-FtsA and MinCDE Oscillatory Machinery",
        analytical_modality: str = "protocell-ftsz-cleavage-constriction",
        equatorial_constriction_pinching_force_pN: float = 34.0,
        min_protein_pole_to_pole_oscillation_period_s: float = 48.0,
        symmetric_daughter_vesicle_yield_pct: float = 88.5,
        ftsz_treadmilling_velocity_nm_per_s: float = 28.0,
        confidence_score: float = 0.994,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SyntheticCellDivisionFtszConstrictionStudy:
        study = SyntheticCellDivisionFtszConstrictionStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            equatorial_constriction_pinching_force_pN=equatorial_constriction_pinching_force_pN,
            min_protein_pole_to_pole_oscillation_period_s=min_protein_pole_to_pole_oscillation_period_s,
            symmetric_daughter_vesicle_yield_pct=symmetric_daughter_vesicle_yield_pct,
            ftsz_treadmilling_velocity_nm_per_s=ftsz_treadmilling_velocity_nm_per_s,
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
    ) -> SyntheticCellDivisionFtszConstrictionItemProfile:
        item = SyntheticCellDivisionFtszConstrictionItemProfile(
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
    ) -> SyntheticCellDivisionFtszConstrictionMetricTrace:
        trace = SyntheticCellDivisionFtszConstrictionMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SyntheticCellDivisionFtszConstrictionStudy]:
        stmt = (
            select(SyntheticCellDivisionFtszConstrictionStudy)
            .where(SyntheticCellDivisionFtszConstrictionStudy.id == study_id)
            .options(
                selectinload(SyntheticCellDivisionFtszConstrictionStudy.item_profiles),
                selectinload(SyntheticCellDivisionFtszConstrictionStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[SyntheticCellDivisionFtszConstrictionStudy]:
        stmt = (
            select(SyntheticCellDivisionFtszConstrictionStudy)
            .order_by(SyntheticCellDivisionFtszConstrictionStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(SyntheticCellDivisionFtszConstrictionStudy.item_profiles),
                selectinload(SyntheticCellDivisionFtszConstrictionStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
