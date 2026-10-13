"""Repository for Phase 462: Autonomous Living Biomaterial Engineered Bacterial Cellulose Scaffold Cross-Linking Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.bacterial_cellulose_scaffold_crosslinking import (
    BacterialCelluloseScaffoldStudy,
    BacterialCelluloseScaffoldItemProfile,
    BacterialCelluloseScaffoldMetricTrace,
)


class BacterialCelluloseScaffoldRepository:
    """Database operations for Autonomous Living Biomaterial Engineered Bacterial Cellulose Scaffold Cross-Linking Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Komagataeibacter xylinus Pellicle Hydrogel with Genetically Encoded SpyTag/SpyCatcher Nodes",
        analytical_modality: str = "living-bacterial-cellulose",
        youngs_elastic_modulus_megapascals: float = 42.5,
        microfibril_crystallinity_index: float = 0.865,
        tensile_fracture_toughness_kj_per_m2: float = 18.4,
        water_retention_swelling_ratio: float = 14.2,
        confidence_score: float = 0.988,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> BacterialCelluloseScaffoldStudy:
        study = BacterialCelluloseScaffoldStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            youngs_elastic_modulus_megapascals=youngs_elastic_modulus_megapascals,
            microfibril_crystallinity_index=microfibril_crystallinity_index,
            tensile_fracture_toughness_kj_per_m2=tensile_fracture_toughness_kj_per_m2,
            water_retention_swelling_ratio=water_retention_swelling_ratio,
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
    ) -> BacterialCelluloseScaffoldItemProfile:
        item = BacterialCelluloseScaffoldItemProfile(
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
    ) -> BacterialCelluloseScaffoldMetricTrace:
        trace = BacterialCelluloseScaffoldMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[BacterialCelluloseScaffoldStudy]:
        result = await self.session.execute(
            select(BacterialCelluloseScaffoldStudy)
            .options(
                selectinload(BacterialCelluloseScaffoldStudy.item_profiles),
                selectinload(BacterialCelluloseScaffoldStudy.metric_traces),
            )
            .where(BacterialCelluloseScaffoldStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[BacterialCelluloseScaffoldStudy]:
        result = await self.session.execute(
            select(BacterialCelluloseScaffoldStudy)
            .options(
                selectinload(BacterialCelluloseScaffoldStudy.item_profiles),
                selectinload(BacterialCelluloseScaffoldStudy.metric_traces),
            )
            .order_by(BacterialCelluloseScaffoldStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
