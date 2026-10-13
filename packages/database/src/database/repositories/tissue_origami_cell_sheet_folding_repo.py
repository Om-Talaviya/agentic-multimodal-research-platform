"""Repository for Phase 467: Autonomous Living Tissue Origami Programmable 4D Cell-Sheet Self-Folding Mechanics Simulator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.tissue_origami_cell_sheet_folding import (
    TissueOrigamiCellSheetFoldingStudy,
    TissueOrigamiCellSheetFoldingItemProfile,
    TissueOrigamiCellSheetFoldingMetricTrace,
)


class TissueOrigamiCellSheetFoldingRepository:
    """Database operations for Autonomous Living Tissue Origami Programmable 4D Cell-Sheet Self-Folding Mechanics Simulator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Bilayer C2C12 Myoblast / NIH-3T3 Fibroblast Sheet on Thermoresponsive PNIPAM Hydrogel",
        analytical_modality: str = "4d-tissue-origami-folding",
        mean_curvature_folding_radius_mm: float = 1.85,
        interfacial_shear_delamination_strain: float = 0.024,
        programmable_crease_bending_angle_deg: float = 84.5,
        myotube_uniaxial_prestress_kpa: float = 18.2,
        confidence_score: float = 0.993,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> TissueOrigamiCellSheetFoldingStudy:
        study = TissueOrigamiCellSheetFoldingStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            mean_curvature_folding_radius_mm=mean_curvature_folding_radius_mm,
            interfacial_shear_delamination_strain=interfacial_shear_delamination_strain,
            programmable_crease_bending_angle_deg=programmable_crease_bending_angle_deg,
            myotube_uniaxial_prestress_kpa=myotube_uniaxial_prestress_kpa,
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
    ) -> TissueOrigamiCellSheetFoldingItemProfile:
        item = TissueOrigamiCellSheetFoldingItemProfile(
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
    ) -> TissueOrigamiCellSheetFoldingMetricTrace:
        trace = TissueOrigamiCellSheetFoldingMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[TissueOrigamiCellSheetFoldingStudy]:
        result = await self.session.execute(
            select(TissueOrigamiCellSheetFoldingStudy)
            .options(
                selectinload(TissueOrigamiCellSheetFoldingStudy.item_profiles),
                selectinload(TissueOrigamiCellSheetFoldingStudy.metric_traces),
            )
            .where(TissueOrigamiCellSheetFoldingStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[TissueOrigamiCellSheetFoldingStudy]:
        result = await self.session.execute(
            select(TissueOrigamiCellSheetFoldingStudy)
            .options(
                selectinload(TissueOrigamiCellSheetFoldingStudy.item_profiles),
                selectinload(TissueOrigamiCellSheetFoldingStudy.metric_traces),
            )
            .order_by(TissueOrigamiCellSheetFoldingStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
