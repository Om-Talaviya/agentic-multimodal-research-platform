"""
Repository for Phase 166: MicroED Structural Engine.
"""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.microed_structural import (
    DBMicroEDExperiment,
    DBMicroEDDiffractionFrame,
    DBMicroEDAtomicRefinement,
)


class MicroEDStructuralRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_experiment(
        self,
        sample_name: str,
        crystal_system: str,
        electron_voltage_kv: float,
        total_rotation_range_degrees: float,
        resolution_limit_angstrom: float,
        completeness_percent: float,
        r_work: float,
        r_free: float,
        project_id: Optional[uuid.UUID] = None,
    ) -> DBMicroEDExperiment:
        exp = DBMicroEDExperiment(
            sample_name=sample_name,
            crystal_system=crystal_system,
            electron_voltage_kv=electron_voltage_kv,
            total_rotation_range_degrees=total_rotation_range_degrees,
            resolution_limit_angstrom=resolution_limit_angstrom,
            completeness_percent=completeness_percent,
            r_work=r_work,
            r_free=r_free,
            project_id=project_id,
        )
        self.db.add(exp)
        await self.db.commit()
        await self.db.refresh(exp)
        return exp

    async def add_diffraction_frame(
        self,
        experiment_id: uuid.UUID,
        frame_number: int,
        tilt_angle_degrees: float,
        observed_reflections_count: int,
        mean_intensity_sigma_ratio: float,
    ) -> DBMicroEDDiffractionFrame:
        frame = DBMicroEDDiffractionFrame(
            experiment_id=experiment_id,
            frame_number=frame_number,
            tilt_angle_degrees=tilt_angle_degrees,
            observed_reflections_count=observed_reflections_count,
            mean_intensity_sigma_ratio=mean_intensity_sigma_ratio,
        )
        self.db.add(frame)
        await self.db.commit()
        await self.db.refresh(frame)
        return frame

    async def add_refinement(
        self,
        experiment_id: uuid.UUID,
        refinement_cycle: int,
        ramachandran_favored_percent: float,
        clashscore: float,
        electrostatic_potential_peak_density: float,
    ) -> DBMicroEDAtomicRefinement:
        refinement = DBMicroEDAtomicRefinement(
            experiment_id=experiment_id,
            refinement_cycle=refinement_cycle,
            ramachandran_favored_percent=ramachandran_favored_percent,
            clashscore=clashscore,
            electrostatic_potential_peak_density=electrostatic_potential_peak_density,
        )
        self.db.add(refinement)
        await self.db.commit()
        await self.db.refresh(refinement)
        return refinement

    async def get_experiment(self, experiment_id: uuid.UUID) -> Optional[DBMicroEDExperiment]:
        stmt = (
            select(DBMicroEDExperiment)
            .options(
                selectinload(DBMicroEDExperiment.frames),
                selectinload(DBMicroEDExperiment.refinements),
            )
            .where(DBMicroEDExperiment.id == experiment_id)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()
