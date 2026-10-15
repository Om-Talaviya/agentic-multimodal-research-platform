"""Repository for Phase 545: Autonomous Microfluidic High-Density Acoustic Droplet Synthetic DNA Digital Archival Writer & Reader."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.microfluidic_acoustic_droplet_dna_storage import (
    MicrofluidicAcousticDropletDnaStorageStudy,
    MicrofluidicAcousticDropletDnaStorageItemProfile,
    MicrofluidicAcousticDropletDnaStorageMetricTrace,
)


class MicrofluidicAcousticDropletDnaStorageRepository:
    """Database operations for Autonomous Microfluidic High-Density Acoustic Droplet Synthetic DNA Digital Archival Writer & Reader."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Acoustic Ejection Picoliter Well Plate containing Encoded 100-Mbyte Synthetic Oligo Pool with RS ECC",
        analytical_modality: str = "acoustic-droplet-dna-archival",
        dna_archival_data_density_petabytes_per_gram: float = 215.0,
        acoustic_droplet_dispensing_throughput_khz: float = 15.0,
        reed_solomon_error_correction_recovery_pct: float = 100.0,
        per_base_synthesis_accuracy_pct: float = 99.92,
        confidence_score: float = 0.998,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> MicrofluidicAcousticDropletDnaStorageStudy:
        study = MicrofluidicAcousticDropletDnaStorageStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            dna_archival_data_density_petabytes_per_gram=dna_archival_data_density_petabytes_per_gram,
            acoustic_droplet_dispensing_throughput_khz=acoustic_droplet_dispensing_throughput_khz,
            reed_solomon_error_correction_recovery_pct=reed_solomon_error_correction_recovery_pct,
            per_base_synthesis_accuracy_pct=per_base_synthesis_accuracy_pct,
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
    ) -> MicrofluidicAcousticDropletDnaStorageItemProfile:
        item = MicrofluidicAcousticDropletDnaStorageItemProfile(
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
    ) -> MicrofluidicAcousticDropletDnaStorageMetricTrace:
        trace = MicrofluidicAcousticDropletDnaStorageMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[MicrofluidicAcousticDropletDnaStorageStudy]:
        stmt = (
            select(MicrofluidicAcousticDropletDnaStorageStudy)
            .where(MicrofluidicAcousticDropletDnaStorageStudy.id == study_id)
            .options(
                selectinload(MicrofluidicAcousticDropletDnaStorageStudy.item_profiles),
                selectinload(MicrofluidicAcousticDropletDnaStorageStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[MicrofluidicAcousticDropletDnaStorageStudy]:
        stmt = (
            select(MicrofluidicAcousticDropletDnaStorageStudy)
            .order_by(MicrofluidicAcousticDropletDnaStorageStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(MicrofluidicAcousticDropletDnaStorageStudy.item_profiles),
                selectinload(MicrofluidicAcousticDropletDnaStorageStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
