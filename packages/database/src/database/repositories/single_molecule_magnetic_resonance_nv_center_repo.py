"""Repository for Phase 436: Autonomous Diamond NV-Center Nanoscale Single-Molecule Magnetic Resonance Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.single_molecule_magnetic_resonance_nv_center import (
    SingleMoleculeNvCenterNmrStudy,
    SingleMoleculeNvCenterNmrItemProfile,
    SingleMoleculeNvCenterNmrMetricTrace,
)


class SingleMoleculeNvCenterNmrRepository:
    """Database operations for Autonomous Diamond NV-Center Nanoscale Single-Molecule Magnetic Resonance Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Diamond Nitrogen-Vacancy (NV) Center Nanocrystal with Surface Immobilized Ferritin",
        analytical_modality: str = "nv-center-nanoscale-nmr",
        spin_coherence_time_t2_us: float = 145.0,
        magnetic_sensitivity_nT_per_sqrthz: float = 2.45,
        optically_detected_mr_dip_contrast: float = 0.185,
        spatial_standoff_distance_nm: float = 3.2,
        confidence_score: float = 0.992,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SingleMoleculeNvCenterNmrStudy:
        study = SingleMoleculeNvCenterNmrStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            spin_coherence_time_t2_us=spin_coherence_time_t2_us,
            magnetic_sensitivity_nT_per_sqrthz=magnetic_sensitivity_nT_per_sqrthz,
            optically_detected_mr_dip_contrast=optically_detected_mr_dip_contrast,
            spatial_standoff_distance_nm=spatial_standoff_distance_nm,
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
    ) -> SingleMoleculeNvCenterNmrItemProfile:
        item = SingleMoleculeNvCenterNmrItemProfile(
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
    ) -> SingleMoleculeNvCenterNmrMetricTrace:
        trace = SingleMoleculeNvCenterNmrMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SingleMoleculeNvCenterNmrStudy]:
        result = await self.session.execute(
            select(SingleMoleculeNvCenterNmrStudy)
            .options(
                selectinload(SingleMoleculeNvCenterNmrStudy.item_profiles),
                selectinload(SingleMoleculeNvCenterNmrStudy.metric_traces),
            )
            .where(SingleMoleculeNvCenterNmrStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[SingleMoleculeNvCenterNmrStudy]:
        result = await self.session.execute(
            select(SingleMoleculeNvCenterNmrStudy)
            .options(
                selectinload(SingleMoleculeNvCenterNmrStudy.item_profiles),
                selectinload(SingleMoleculeNvCenterNmrStudy.metric_traces),
            )
            .order_by(SingleMoleculeNvCenterNmrStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
