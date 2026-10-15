"""Repository for Phase 537: Autonomous Single-Molecule Magnetic Torque Tweezers (MTT) DNA Supercoiling & Twist Modeler."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.single_molecule_magnetic_torque_tweezer import (
    SingleMoleculeMagneticTorqueTweezerStudy,
    SingleMoleculeMagneticTorqueTweezerItemProfile,
    SingleMoleculeMagneticTorqueTweezerMetricTrace,
)


class SingleMoleculeMagneticTorqueTweezerRepository:
    """Database operations for Autonomous Single-Molecule Magnetic Torque Tweezers (MTT) DNA Supercoiling & Twist Modeler."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        name: str,
        target_specimen: str = "Tethered 10-kb Double-Stranded DNA Molecule with Cylindrical Magnetic Bead in Horizontal Torque Field",
        analytical_modality: str = "magnetic-torque-tweezers-supercoiling",
        torsional_persistence_length_nm: float = 84.0,
        buckling_transition_critical_torque_pN_nm: float = 28.5,
        plectoneme_supercoil_conformation_density: float = 0.052,
        dna_twist_stretch_coupling_constant_pN: float = -95.0,
        confidence_score: float = 0.996,
        status: str = "completed",
        parameters: dict = None,
        summary_report: str = "",
    ) -> SingleMoleculeMagneticTorqueTweezerStudy:
        study = SingleMoleculeMagneticTorqueTweezerStudy(
            name=name,
            target_specimen=target_specimen,
            analytical_modality=analytical_modality,
            torsional_persistence_length_nm=torsional_persistence_length_nm,
            buckling_transition_critical_torque_pN_nm=buckling_transition_critical_torque_pN_nm,
            plectoneme_supercoil_conformation_density=plectoneme_supercoil_conformation_density,
            dna_twist_stretch_coupling_constant_pN=dna_twist_stretch_coupling_constant_pN,
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
    ) -> SingleMoleculeMagneticTorqueTweezerItemProfile:
        item = SingleMoleculeMagneticTorqueTweezerItemProfile(
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
    ) -> SingleMoleculeMagneticTorqueTweezerMetricTrace:
        trace = SingleMoleculeMagneticTorqueTweezerMetricTrace(
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

    async def get_study(self, study_id: UUID) -> Optional[SingleMoleculeMagneticTorqueTweezerStudy]:
        stmt = (
            select(SingleMoleculeMagneticTorqueTweezerStudy)
            .where(SingleMoleculeMagneticTorqueTweezerStudy.id == study_id)
            .options(
                selectinload(SingleMoleculeMagneticTorqueTweezerStudy.item_profiles),
                selectinload(SingleMoleculeMagneticTorqueTweezerStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_studies(self, limit: int = 20) -> List[SingleMoleculeMagneticTorqueTweezerStudy]:
        stmt = (
            select(SingleMoleculeMagneticTorqueTweezerStudy)
            .order_by(SingleMoleculeMagneticTorqueTweezerStudy.created_at.desc())
            .limit(limit)
            .options(
                selectinload(SingleMoleculeMagneticTorqueTweezerStudy.item_profiles),
                selectinload(SingleMoleculeMagneticTorqueTweezerStudy.metric_traces),
            )
        )
        res = await self.session.execute(stmt)
        return list(res.scalars().all())
