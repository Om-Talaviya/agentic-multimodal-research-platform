"""Repository for Phase 441: Autonomous Fenna-Matthews-Olson (FMO) Complex Quantum Exciton Energy Transfer & Coherence Modeler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.photosystem_quantum_coherence_exciton_fmo import (
    PhotosystemQuantumCoherenceStudy,
    PhotosystemQuantumCoherenceItemProfile,
    PhotosystemQuantumCoherenceMetricTrace,
)


class PhotosystemQuantumCoherenceRepository:
    """Database operations for Autonomous Fenna-Matthews-Olson (FMO) Complex Quantum Exciton Energy Transfer & Coherence Modeler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Green Sulfur Bacteria Chlorobium tepidum FMO Bacteriochlorophyll Trimer",
        analytical_modality: str = "quantum-exciton-fmo",
        exciton_transfer_efficiency_ratio: float = 0.991,
        quantum_coherence_lifetime_fs: float = 420.0,
        site_energy_disorder_cm_inv: float = 85.0,
        sink_bchl_trapping_rate_ps_inv: float = 1.85,
        confidence_score: float = 0.989,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> PhotosystemQuantumCoherenceStudy:
        study = PhotosystemQuantumCoherenceStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            exciton_transfer_efficiency_ratio=exciton_transfer_efficiency_ratio,
            quantum_coherence_lifetime_fs=quantum_coherence_lifetime_fs,
            site_energy_disorder_cm_inv=site_energy_disorder_cm_inv,
            sink_bchl_trapping_rate_ps_inv=sink_bchl_trapping_rate_ps_inv,
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
    ) -> PhotosystemQuantumCoherenceItemProfile:
        item = PhotosystemQuantumCoherenceItemProfile(
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
    ) -> PhotosystemQuantumCoherenceMetricTrace:
        trace = PhotosystemQuantumCoherenceMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[PhotosystemQuantumCoherenceStudy]:
        result = await self.session.execute(
            select(PhotosystemQuantumCoherenceStudy)
            .options(
                selectinload(PhotosystemQuantumCoherenceStudy.item_profiles),
                selectinload(PhotosystemQuantumCoherenceStudy.metric_traces),
            )
            .where(PhotosystemQuantumCoherenceStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[PhotosystemQuantumCoherenceStudy]:
        result = await self.session.execute(
            select(PhotosystemQuantumCoherenceStudy)
            .options(
                selectinload(PhotosystemQuantumCoherenceStudy.item_profiles),
                selectinload(PhotosystemQuantumCoherenceStudy.metric_traces),
            )
            .order_by(PhotosystemQuantumCoherenceStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
