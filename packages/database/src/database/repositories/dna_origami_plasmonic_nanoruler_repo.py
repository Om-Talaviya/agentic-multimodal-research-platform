"""Repository for Phase 506: Autonomous DNA Origami Reconfigurable Plasmonic Nanoruler Distance Calibrator."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.dna_origami_plasmonic_nanoruler import (
    DnaOrigamiPlasmonicNanorulerStudy,
    DnaOrigamiPlasmonicNanorulerItemProfile,
    DnaOrigamiPlasmonicNanorulerMetricTrace,
)


class DnaOrigamiPlasmonicNanorulerRepository:
    """Database operations for Autonomous DNA Origami Reconfigurable Plasmonic Nanoruler Distance Calibrator."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Scaffolded DNA Origami 12-Helix Bundle with Gold Nanoparticle Dimer Heterostructure",
        analytical_modality: str = "dna-origami-plasmonic-nanoruler",
        plasmonic_coupling_resonance_wavelength_nm: float = 648.5,
        interparticle_gap_distance_nm: float = 3.4,
        single_molecule_fluorescence_enhancement_factor: float = 128.0,
        conformational_nanoruler_accuracy_pm: float = 45.0,
        confidence_score: float = 0.995,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> DnaOrigamiPlasmonicNanorulerStudy:
        study = DnaOrigamiPlasmonicNanorulerStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            plasmonic_coupling_resonance_wavelength_nm=plasmonic_coupling_resonance_wavelength_nm,
            interparticle_gap_distance_nm=interparticle_gap_distance_nm,
            single_molecule_fluorescence_enhancement_factor=single_molecule_fluorescence_enhancement_factor,
            conformational_nanoruler_accuracy_pm=conformational_nanoruler_accuracy_pm,
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
    ) -> DnaOrigamiPlasmonicNanorulerItemProfile:
        item = DnaOrigamiPlasmonicNanorulerItemProfile(
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
    ) -> DnaOrigamiPlasmonicNanorulerMetricTrace:
        trace = DnaOrigamiPlasmonicNanorulerMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[DnaOrigamiPlasmonicNanorulerStudy]:
        result = await self.session.execute(
            select(DnaOrigamiPlasmonicNanorulerStudy)
            .options(
                selectinload(DnaOrigamiPlasmonicNanorulerStudy.item_profiles),
                selectinload(DnaOrigamiPlasmonicNanorulerStudy.metric_traces),
            )
            .where(DnaOrigamiPlasmonicNanorulerStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DnaOrigamiPlasmonicNanorulerStudy]:
        result = await self.session.execute(
            select(DnaOrigamiPlasmonicNanorulerStudy)
            .options(
                selectinload(DnaOrigamiPlasmonicNanorulerStudy.item_profiles),
                selectinload(DnaOrigamiPlasmonicNanorulerStudy.metric_traces),
            )
            .order_by(DnaOrigamiPlasmonicNanorulerStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
