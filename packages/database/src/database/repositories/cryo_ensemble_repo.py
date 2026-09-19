"""Repository for Cryo-EM Flexible Backbone Ensemble data access (Phase 97)."""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.models.cryo_ensemble import (
    DBCryoEmEnsemble,
    DBCryoConformationalState,
    DBFreeEnergyTransition,
)


class CryoEnsembleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_ensemble(
        self,
        workspace_id: uuid.UUID,
        target_protein: str,
        pdb_reference_id: str,
        density_map_resolution_angstrom: float = 2.65,
        latent_space_dimensions: int = 3,
        total_conformational_states: int = 4,
        flexibility_rmsd_angstrom: float = 3.82,
        ensemble_metadata: Optional[Dict[str, Any]] = None,
    ) -> DBCryoEmEnsemble:
        ens = DBCryoEmEnsemble(
            workspace_id=workspace_id,
            target_protein=target_protein,
            pdb_reference_id=pdb_reference_id,
            density_map_resolution_angstrom=density_map_resolution_angstrom,
            latent_space_dimensions=latent_space_dimensions,
            total_conformational_states=total_conformational_states,
            flexibility_rmsd_angstrom=flexibility_rmsd_angstrom,
            ensemble_metadata=ensemble_metadata or {},
        )
        self.session.add(ens)
        await self.session.commit()
        await self.session.refresh(ens)
        return ens

    async def add_state(
        self,
        ensemble_id: uuid.UUID,
        state_label: str,
        population_percentage: float,
        relative_free_energy_kcal_mol: float,
        backbone_rmsd_to_reference: float,
        binding_pocket_volume_angstrom3: float = 740.0,
    ) -> DBCryoConformationalState:
        state = DBCryoConformationalState(
            ensemble_id=ensemble_id,
            state_label=state_label,
            population_percentage=population_percentage,
            relative_free_energy_kcal_mol=relative_free_energy_kcal_mol,
            backbone_rmsd_to_reference=backbone_rmsd_to_reference,
            binding_pocket_volume_angstrom3=binding_pocket_volume_angstrom3,
        )
        self.session.add(state)
        await self.session.commit()
        await self.session.refresh(state)
        return state

    async def add_transition(
        self,
        ensemble_id: uuid.UUID,
        from_state: str,
        to_state: str,
        energy_barrier_kcal_mol: float,
        transition_rate_per_sec: float = 4.5e4,
    ) -> DBFreeEnergyTransition:
        trans = DBFreeEnergyTransition(
            ensemble_id=ensemble_id,
            from_state=from_state,
            to_state=to_state,
            energy_barrier_kcal_mol=energy_barrier_kcal_mol,
            transition_rate_per_sec=transition_rate_per_sec,
        )
        self.session.add(trans)
        await self.session.commit()
        await self.session.refresh(trans)
        return trans

    async def get_ensemble(self, ensemble_id: uuid.UUID) -> Optional[DBCryoEmEnsemble]:
        stmt = (
            select(DBCryoEmEnsemble)
            .options(
                selectinload(DBCryoEmEnsemble.states),
                selectinload(DBCryoEmEnsemble.transitions),
            )
            .where(DBCryoEmEnsemble.id == ensemble_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
