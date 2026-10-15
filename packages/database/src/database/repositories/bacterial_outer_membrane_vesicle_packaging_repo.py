"""Repository for Phase 530: Autonomous Bacterial Outer Membrane Vesicle (OMV) Biogenesis & Cargo Sorting Predictor."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.bacterial_outer_membrane_vesicle_packaging import (
    BacterialOuterMembraneVesiclePackagingStudy,
    BacterialOuterMembraneVesiclePackagingItemProfile,
    BacterialOuterMembraneVesiclePackagingMetricTrace,
)


class BacterialOuterMembraneVesiclePackagingRepository:
    """Database operations for Autonomous Bacterial Outer Membrane Vesicle (OMV) Biogenesis & Cargo Sorting Predictor."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Hyper-Vesiculating Engineered Pseudomonas aeruginosa Strain PAO1 Membrane Fractions",
        analytical_modality: str = "omv-biogenesis-cargo-sorting",
        vesiculation_rate_omv_per_cell_hr: float = 145.0,
        cargo_virulence_factor_enrichment_ratio: float = 8.4,
        vesicle_average_hydrodynamic_diameter_nm: float = 82.5,
        lps_phospholipid_asymmetry_index: float = 0.94,
        confidence_score: float = 0.992,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> BacterialOuterMembraneVesiclePackagingStudy:
        study = BacterialOuterMembraneVesiclePackagingStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            vesiculation_rate_omv_per_cell_hr=vesiculation_rate_omv_per_cell_hr,
            cargo_virulence_factor_enrichment_ratio=cargo_virulence_factor_enrichment_ratio,
            vesicle_average_hydrodynamic_diameter_nm=vesicle_average_hydrodynamic_diameter_nm,
            lps_phospholipid_asymmetry_index=lps_phospholipid_asymmetry_index,
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
    ) -> BacterialOuterMembraneVesiclePackagingItemProfile:
        item = BacterialOuterMembraneVesiclePackagingItemProfile(
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
    ) -> BacterialOuterMembraneVesiclePackagingMetricTrace:
        trace = BacterialOuterMembraneVesiclePackagingMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[BacterialOuterMembraneVesiclePackagingStudy]:
        stmt = (
            select(BacterialOuterMembraneVesiclePackagingStudy)
            .where(BacterialOuterMembraneVesiclePackagingStudy.id == study_id)
            .options(
                selectinload(BacterialOuterMembraneVesiclePackagingStudy.item_profiles),
                selectinload(BacterialOuterMembraneVesiclePackagingStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[BacterialOuterMembraneVesiclePackagingStudy]:
        stmt = (
            select(BacterialOuterMembraneVesiclePackagingStudy)
            .order_by(BacterialOuterMembraneVesiclePackagingStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(BacterialOuterMembraneVesiclePackagingStudy.item_profiles),
                selectinload(BacterialOuterMembraneVesiclePackagingStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
