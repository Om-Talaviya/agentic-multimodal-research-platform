"""Repository for Phase 536: Autonomous In-Situ Cryo-ET Endoplasmic Reticulum-Mitochondria Membrane Curvature Elastic Stress Profiler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.cryoet_organelle_membrane_curvature_stress import (
    CryoetOrganelleMembraneCurvatureStressStudy,
    CryoetOrganelleMembraneCurvatureStressItemProfile,
    CryoetOrganelleMembraneCurvatureStressMetricTrace,
)


class CryoetOrganelleMembraneCurvatureStressRepository:
    """Database operations for Autonomous In-Situ Cryo-ET Endoplasmic Reticulum-Mitochondria Membrane Curvature Elastic Stress Profiler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Vitrified Primary Murine Hepatocyte Lamella showing In-Situ MAM (Mitochondria-Associated ER Membrane) Junctions",
        analytical_modality: str = "cryoet-organelle-membrane-stress",
        membrane_bending_modulus_kbT: float = 22.5,
        mam_intermembrane_contact_distance_nm: float = 14.2,
        principal_curvature_radius_nm: float = 18.4,
        lipid_packing_defect_density_per_nm2: float = 0.038,
        confidence_score: float = 0.993,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> CryoetOrganelleMembraneCurvatureStressStudy:
        study = CryoetOrganelleMembraneCurvatureStressStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            membrane_bending_modulus_kbT=membrane_bending_modulus_kbT,
            mam_intermembrane_contact_distance_nm=mam_intermembrane_contact_distance_nm,
            principal_curvature_radius_nm=principal_curvature_radius_nm,
            lipid_packing_defect_density_per_nm2=lipid_packing_defect_density_per_nm2,
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
    ) -> CryoetOrganelleMembraneCurvatureStressItemProfile:
        item = CryoetOrganelleMembraneCurvatureStressItemProfile(
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
    ) -> CryoetOrganelleMembraneCurvatureStressMetricTrace:
        trace = CryoetOrganelleMembraneCurvatureStressMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[CryoetOrganelleMembraneCurvatureStressStudy]:
        stmt = (
            select(CryoetOrganelleMembraneCurvatureStressStudy)
            .where(CryoetOrganelleMembraneCurvatureStressStudy.id == study_id)
            .options(
                selectinload(CryoetOrganelleMembraneCurvatureStressStudy.item_profiles),
                selectinload(CryoetOrganelleMembraneCurvatureStressStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[CryoetOrganelleMembraneCurvatureStressStudy]:
        stmt = (
            select(CryoetOrganelleMembraneCurvatureStressStudy)
            .order_by(CryoetOrganelleMembraneCurvatureStressStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(CryoetOrganelleMembraneCurvatureStressStudy.item_profiles),
                selectinload(CryoetOrganelleMembraneCurvatureStressStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
