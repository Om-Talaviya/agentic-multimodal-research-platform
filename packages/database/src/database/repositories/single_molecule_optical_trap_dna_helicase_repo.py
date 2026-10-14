"""Repository for Phase 512: Autonomous Single-Molecule Dual-Trap Optical Tweezers DNA Helicase Unwinding Stepper."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.single_molecule_optical_trap_dna_helicase import (
    SingleMoleculeOpticalTrapDnaHelicaseStudy,
    SingleMoleculeOpticalTrapDnaHelicaseItemProfile,
    SingleMoleculeOpticalTrapDnaHelicaseMetricTrace,
)


class SingleMoleculeOpticalTrapDnaHelicaseRepository:
    """Database operations for Autonomous Single-Molecule Dual-Trap Optical Tweezers DNA Helicase Unwinding Stepper."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Dual-Beam Optical Trap Tethered dsDNA Hairpin with Recombinant Human Bloom Syndrome Helicase",
        analytical_modality: str = "optical-trap-helicase-unwinding",
        helicase_stepping_velocity_bp_per_s: float = 48.5,
        atp_fuel_efficiency_bp_per_atp: float = 1.0,
        strand_unwinding_processivity_bp: float = 1450.0,
        sub_nanometer_step_size_bp: float = 1.0,
        confidence_score: float = 0.996,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SingleMoleculeOpticalTrapDnaHelicaseStudy:
        study = SingleMoleculeOpticalTrapDnaHelicaseStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            helicase_stepping_velocity_bp_per_s=helicase_stepping_velocity_bp_per_s,
            atp_fuel_efficiency_bp_per_atp=atp_fuel_efficiency_bp_per_atp,
            strand_unwinding_processivity_bp=strand_unwinding_processivity_bp,
            sub_nanometer_step_size_bp=sub_nanometer_step_size_bp,
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
    ) -> SingleMoleculeOpticalTrapDnaHelicaseItemProfile:
        item = SingleMoleculeOpticalTrapDnaHelicaseItemProfile(
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
    ) -> SingleMoleculeOpticalTrapDnaHelicaseMetricTrace:
        trace = SingleMoleculeOpticalTrapDnaHelicaseMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SingleMoleculeOpticalTrapDnaHelicaseStudy]:
        result = await self.session.execute(
            select(SingleMoleculeOpticalTrapDnaHelicaseStudy)
            .options(
                selectinload(SingleMoleculeOpticalTrapDnaHelicaseStudy.item_profiles),
                selectinload(SingleMoleculeOpticalTrapDnaHelicaseStudy.metric_traces),
            )
            .where(SingleMoleculeOpticalTrapDnaHelicaseStudy.id == study_id)
        )
        return result.scalars().first()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[SingleMoleculeOpticalTrapDnaHelicaseStudy]:
        result = await self.session.execute(
            select(SingleMoleculeOpticalTrapDnaHelicaseStudy)
            .options(
                selectinload(SingleMoleculeOpticalTrapDnaHelicaseStudy.item_profiles),
                selectinload(SingleMoleculeOpticalTrapDnaHelicaseStudy.metric_traces),
            )
            .order_by(SingleMoleculeOpticalTrapDnaHelicaseStudy.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
