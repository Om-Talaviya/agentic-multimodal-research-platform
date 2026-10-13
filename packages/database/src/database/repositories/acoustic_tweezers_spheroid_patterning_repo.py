"""Repository for Phase 465: Autonomous Microfluidic Acoustic Tweezers Multicellular Spheroid Patterning & Cytoskeletal Stress Engine."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.acoustic_tweezers_spheroid_patterning import (
    AcousticTweezersSpheroidPatterningStudy,
    AcousticTweezersSpheroidPatterningItemProfile,
    AcousticTweezersSpheroidPatterningMetricTrace,
)


class AcousticTweezersSpheroidPatterningRepository:
    """Database operations for Autonomous Microfluidic Acoustic Tweezers Multicellular Spheroid Patterning & Cytoskeletal Stress Engine."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "3D MCF-7 Breast Tumor Spheroid Array patterned in 2.5 MHz Standing Bulk Acoustic Wave Resonator",
        analytical_modality: str = "acoustic-spheroid-patterning",
        acoustic_radiation_force_pN: float = 42.5,
        spheroid_diameter_uniformity_cv: float = 0.048,
        cytoskeletal_f_actin_alignment_index: float = 0.885,
        acoustic_trapping_node_stability: float = 0.992,
        confidence_score: float = 0.991,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> AcousticTweezersSpheroidPatterningStudy:
        study = AcousticTweezersSpheroidPatterningStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            acoustic_radiation_force_pN=acoustic_radiation_force_pN,
            spheroid_diameter_uniformity_cv=spheroid_diameter_uniformity_cv,
            cytoskeletal_f_actin_alignment_index=cytoskeletal_f_actin_alignment_index,
            acoustic_trapping_node_stability=acoustic_trapping_node_stability,
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
    ) -> AcousticTweezersSpheroidPatterningItemProfile:
        item = AcousticTweezersSpheroidPatterningItemProfile(
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
    ) -> AcousticTweezersSpheroidPatterningMetricTrace:
        trace = AcousticTweezersSpheroidPatterningMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[AcousticTweezersSpheroidPatterningStudy]:
        result = await self.session.execute(
            select(AcousticTweezersSpheroidPatterningStudy)
            .options(
                selectinload(AcousticTweezersSpheroidPatterningStudy.item_profiles),
                selectinload(AcousticTweezersSpheroidPatterningStudy.metric_traces),
            )
            .where(AcousticTweezersSpheroidPatterningStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[AcousticTweezersSpheroidPatterningStudy]:
        result = await self.session.execute(
            select(AcousticTweezersSpheroidPatterningStudy)
            .options(
                selectinload(AcousticTweezersSpheroidPatterningStudy.item_profiles),
                selectinload(AcousticTweezersSpheroidPatterningStudy.metric_traces),
            )
            .order_by(AcousticTweezersSpheroidPatterningStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
