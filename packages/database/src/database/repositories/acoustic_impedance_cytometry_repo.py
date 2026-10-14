"""Repository for Phase 475: Autonomous Multiplexed Bio-Acoustic Cellular Impedance Flow Cytometry Classifier."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.acoustic_impedance_cytometry import (
    AcousticImpedanceCytometryStudy,
    AcousticImpedanceCytometryItemProfile,
    AcousticImpedanceCytometryMetricTrace,
)


class AcousticImpedanceCytometryRepository:
    """Database operations for Autonomous Multiplexed Bio-Acoustic Cellular Impedance Flow Cytometry Classifier."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "High-Throughput Microfluidic Coplanar Electrode Microchannel with Circulating Tumor Cell Suspensions",
        analytical_modality: str = "acoustic-impedance-cytometry",
        dielectric_membrane_capacitance_uF_per_cm2: float = 1.25,
        cytoplasm_conductivity_S_per_m: float = 0.68,
        acoustic_focusing_transit_time_uniformity_cv: float = 0.032,
        single_cell_classification_accuracy: float = 0.985,
        confidence_score: float = 0.992,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> AcousticImpedanceCytometryStudy:
        study = AcousticImpedanceCytometryStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            dielectric_membrane_capacitance_uF_per_cm2=dielectric_membrane_capacitance_uF_per_cm2,
            cytoplasm_conductivity_S_per_m=cytoplasm_conductivity_S_per_m,
            acoustic_focusing_transit_time_uniformity_cv=acoustic_focusing_transit_time_uniformity_cv,
            single_cell_classification_accuracy=single_cell_classification_accuracy,
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
    ) -> AcousticImpedanceCytometryItemProfile:
        item = AcousticImpedanceCytometryItemProfile(
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
    ) -> AcousticImpedanceCytometryMetricTrace:
        trace = AcousticImpedanceCytometryMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[AcousticImpedanceCytometryStudy]:
        result = await self.session.execute(
            select(AcousticImpedanceCytometryStudy)
            .options(
                selectinload(AcousticImpedanceCytometryStudy.item_profiles),
                selectinload(AcousticImpedanceCytometryStudy.metric_traces),
            )
            .where(AcousticImpedanceCytometryStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[AcousticImpedanceCytometryStudy]:
        result = await self.session.execute(
            select(AcousticImpedanceCytometryStudy)
            .options(
                selectinload(AcousticImpedanceCytometryStudy.item_profiles),
                selectinload(AcousticImpedanceCytometryStudy.metric_traces),
            )
            .order_by(AcousticImpedanceCytometryStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
