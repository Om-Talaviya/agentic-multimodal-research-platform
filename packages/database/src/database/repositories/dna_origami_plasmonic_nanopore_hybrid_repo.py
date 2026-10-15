"""Repository for Phase 533: Autonomous DNA Origami Plasmonic Hotspot Nanopore Single-Molecule Optical Tweezers Integrator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.dna_origami_plasmonic_nanopore_hybrid import (
    DnaOrigamiPlasmonicNanoporeHybridStudy,
    DnaOrigamiPlasmonicNanoporeHybridItemProfile,
    DnaOrigamiPlasmonicNanoporeHybridMetricTrace,
)


class DnaOrigamiPlasmonicNanoporeHybridRepository:
    """Database operations for Autonomous DNA Origami Plasmonic Hotspot Nanopore Single-Molecule Optical Tweezers Integrator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Hybrid Gold Bowtie Nanoantenna Mounted on 3D DNA Origami Funnel over 5nm Solid-State Nanopore",
        analytical_modality: str = "plasmonic-nanopore-optical-tweezers",
        optical_trapping_stiffness_fN_nm_mW: float = 18.2,
        electromagnetic_hotspot_field_enhancement: float = 450.0,
        single_protein_dwell_extension_factor: float = 64.0,
        ionic_optical_cross_correlation_peak: float = 0.91,
        confidence_score: float = 0.996,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> DnaOrigamiPlasmonicNanoporeHybridStudy:
        study = DnaOrigamiPlasmonicNanoporeHybridStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            optical_trapping_stiffness_fN_nm_mW=optical_trapping_stiffness_fN_nm_mW,
            electromagnetic_hotspot_field_enhancement=electromagnetic_hotspot_field_enhancement,
            single_protein_dwell_extension_factor=single_protein_dwell_extension_factor,
            ionic_optical_cross_correlation_peak=ionic_optical_cross_correlation_peak,
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
    ) -> DnaOrigamiPlasmonicNanoporeHybridItemProfile:
        item = DnaOrigamiPlasmonicNanoporeHybridItemProfile(
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
    ) -> DnaOrigamiPlasmonicNanoporeHybridMetricTrace:
        trace = DnaOrigamiPlasmonicNanoporeHybridMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[DnaOrigamiPlasmonicNanoporeHybridStudy]:
        stmt = (
            select(DnaOrigamiPlasmonicNanoporeHybridStudy)
            .where(DnaOrigamiPlasmonicNanoporeHybridStudy.id == study_id)
            .options(
                selectinload(DnaOrigamiPlasmonicNanoporeHybridStudy.item_profiles),
                selectinload(DnaOrigamiPlasmonicNanoporeHybridStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[DnaOrigamiPlasmonicNanoporeHybridStudy]:
        stmt = (
            select(DnaOrigamiPlasmonicNanoporeHybridStudy)
            .order_by(DnaOrigamiPlasmonicNanoporeHybridStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(DnaOrigamiPlasmonicNanoporeHybridStudy.item_profiles),
                selectinload(DnaOrigamiPlasmonicNanoporeHybridStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
