"""Repository for Membrane Permeability & PAMPA QSAR."""

import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.models.membrane_permeability import (
    DBPAMPAPermeabilityStudy,
    DBMembraneDiffusivityRecord,
    DBPermeabilityQSARProfile,
)


class MembranePermeabilityRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_study(
        self,
        molecule_name: str,
        smiles: str,
        molecular_weight: float,
        logp: float,
        tpsa: float,
        papp_cm_per_s: float,
        permeability_class: str,
    ) -> DBPAMPAPermeabilityStudy:
        study = DBPAMPAPermeabilityStudy(
            molecule_name=molecule_name,
            smiles=smiles,
            molecular_weight=molecular_weight,
            logp=logp,
            tpsa=tpsa,
            papp_cm_per_s=papp_cm_per_s,
            permeability_class=permeability_class,
        )
        self.db.add(study)
        await self.db.commit()
        await self.db.refresh(study)
        return study

    async def add_diffusivity_record(
        self,
        study_id: uuid.UUID,
        bilayer_depth_angstrom: float,
        free_energy_barrier_kcal_mol: float,
        local_diffusion_coefficient: float,
    ) -> DBMembraneDiffusivityRecord:
        rec = DBMembraneDiffusivityRecord(
            study_id=study_id,
            bilayer_depth_angstrom=bilayer_depth_angstrom,
            free_energy_barrier_kcal_mol=free_energy_barrier_kcal_mol,
            local_diffusion_coefficient=local_diffusion_coefficient,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def add_qsar_profile(
        self,
        study_id: uuid.UUID,
        h_bond_donors: int,
        h_bond_acceptors: int,
        rotatable_bonds: int,
        predicted_pampa_score: float,
        is_blood_brain_barrier_permeable: bool,
    ) -> DBPermeabilityQSARProfile:
        prof = DBPermeabilityQSARProfile(
            study_id=study_id,
            h_bond_donors=h_bond_donors,
            h_bond_acceptors=h_bond_acceptors,
            rotatable_bonds=rotatable_bonds,
            predicted_pampa_score=predicted_pampa_score,
            is_blood_brain_barrier_permeable=is_blood_brain_barrier_permeable,
        )
        self.db.add(prof)
        await self.db.commit()
        await self.db.refresh(prof)
        return prof

    async def get_study_with_details(self, study_id: uuid.UUID) -> Optional[DBPAMPAPermeabilityStudy]:
        stmt = (
            select(DBPAMPAPermeabilityStudy)
            .where(DBPAMPAPermeabilityStudy.id == study_id)
            .options(
                selectinload(DBPAMPAPermeabilityStudy.diffusivity_records),
                selectinload(DBPAMPAPermeabilityStudy.qsar_profiles),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
