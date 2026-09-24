"""Repository for Single-Molecule FRET (Phase 160)."""

import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.single_molecule_fret import (
    DBSingleMoleculeFRETStudy,
    DBFRETKineticStateTransition,
    DBFluorophorePhotobleachingTrajectory,
)


class SingleMoleculeFRETRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_study(
        self,
        biomolecule_name: str,
        donor_fluorophore: str,
        acceptor_fluorophore: str,
        forster_distance_r0_nm: float,
        molecules_analyzed_count: int,
        mean_fret_efficiency: float,
        transition_rate_k_open_s: float,
        transition_rate_k_close_s: float,
    ) -> DBSingleMoleculeFRETStudy:
        study = DBSingleMoleculeFRETStudy(
            id=uuid.uuid4(),
            biomolecule_name=biomolecule_name,
            donor_fluorophore=donor_fluorophore,
            acceptor_fluorophore=acceptor_fluorophore,
            forster_distance_r0_nm=forster_distance_r0_nm,
            molecules_analyzed_count=molecules_analyzed_count,
            mean_fret_efficiency=mean_fret_efficiency,
            transition_rate_k_open_s=transition_rate_k_open_s,
            transition_rate_k_close_s=transition_rate_k_close_s,
        )
        self.db.add(study)
        await self.db.commit()
        await self.db.refresh(study)
        return study

    async def add_state_transition(
        self,
        study_id: uuid.UUID,
        state_label: str,
        fret_efficiency_peak: float,
        mean_dwell_time_ms: float,
        state_occupancy_percentage: float,
        apparent_distance_angstrom: float,
    ) -> DBFRETKineticStateTransition:
        rec = DBFRETKineticStateTransition(
            id=uuid.uuid4(),
            study_id=study_id,
            state_label=state_label,
            fret_efficiency_peak=fret_efficiency_peak,
            mean_dwell_time_ms=mean_dwell_time_ms,
            state_occupancy_percentage=state_occupancy_percentage,
            apparent_distance_angstrom=apparent_distance_angstrom,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def add_trajectory(
        self,
        study_id: uuid.UUID,
        molecule_index: int,
        donor_lifetime_seconds: float,
        acceptor_lifetime_seconds: float,
        total_transitions_observed: int,
        single_step_photobleaching: bool,
    ) -> DBFluorophorePhotobleachingTrajectory:
        rec = DBFluorophorePhotobleachingTrajectory(
            id=uuid.uuid4(),
            study_id=study_id,
            molecule_index=molecule_index,
            donor_lifetime_seconds=donor_lifetime_seconds,
            acceptor_lifetime_seconds=acceptor_lifetime_seconds,
            total_transitions_observed=total_transitions_observed,
            single_step_photobleaching=single_step_photobleaching,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def get_study_with_details(self, study_id: uuid.UUID) -> Optional[DBSingleMoleculeFRETStudy]:
        stmt = (
            select(DBSingleMoleculeFRETStudy)
            .where(DBSingleMoleculeFRETStudy.id == study_id)
            .options(
                selectinload(DBSingleMoleculeFRETStudy.state_transitions),
                selectinload(DBSingleMoleculeFRETStudy.trajectories),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
