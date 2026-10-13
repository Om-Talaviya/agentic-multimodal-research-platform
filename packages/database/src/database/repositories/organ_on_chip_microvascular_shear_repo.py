"""Repository for Phase 458: Autonomous Organ-on-Chip Multi-Tissue Microvascular Fluid Shear Stress Perfusion Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.organ_on_chip_microvascular_shear import (
    OrganOnChipMicrovascularShearStudy,
    OrganOnChipMicrovascularShearItemProfile,
    OrganOnChipMicrovascularShearMetricTrace,
)


class OrganOnChipMicrovascularShearRepository:
    """Database operations for Autonomous Organ-on-Chip Multi-Tissue Microvascular Fluid Shear Stress Perfusion Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Dual-Channel Microfluidic Blood-Brain Barrier Chip with Pericytes and Endothelial Shear",
        analytical_modality: str = "microvascular-fluid-shear",
        wall_shear_stress_dynes_per_cm2: float = 14.8,
        transendothelial_electrical_resistance_teer_ohm_cm2: float = 1850.0,
        dextran_permeability_coefficient_cm_per_s: float = 1.2e-05,
        endothelial_alignment_angle_std_deg: float = 8.4,
        confidence_score: float = 0.992,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> OrganOnChipMicrovascularShearStudy:
        study = OrganOnChipMicrovascularShearStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            wall_shear_stress_dynes_per_cm2=wall_shear_stress_dynes_per_cm2,
            transendothelial_electrical_resistance_teer_ohm_cm2=transendothelial_electrical_resistance_teer_ohm_cm2,
            dextran_permeability_coefficient_cm_per_s=dextran_permeability_coefficient_cm_per_s,
            endothelial_alignment_angle_std_deg=endothelial_alignment_angle_std_deg,
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
    ) -> OrganOnChipMicrovascularShearItemProfile:
        item = OrganOnChipMicrovascularShearItemProfile(
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
    ) -> OrganOnChipMicrovascularShearMetricTrace:
        trace = OrganOnChipMicrovascularShearMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[OrganOnChipMicrovascularShearStudy]:
        result = await self.session.execute(
            select(OrganOnChipMicrovascularShearStudy)
            .options(
                selectinload(OrganOnChipMicrovascularShearStudy.item_profiles),
                selectinload(OrganOnChipMicrovascularShearStudy.metric_traces),
            )
            .where(OrganOnChipMicrovascularShearStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[OrganOnChipMicrovascularShearStudy]:
        result = await self.session.execute(
            select(OrganOnChipMicrovascularShearStudy)
            .options(
                selectinload(OrganOnChipMicrovascularShearStudy.item_profiles),
                selectinload(OrganOnChipMicrovascularShearStudy.metric_traces),
            )
            .order_by(OrganOnChipMicrovascularShearStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
