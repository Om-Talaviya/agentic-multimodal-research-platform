"""
Repository for Phase 134: Non-Coding RNA Riboswitch Kinetic Switch Simulator & Aptamer Free-Energy Folding Engine.
"""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from database.models.riboswitch_kinetics import (
    DBRiboswitchCircuit,
    DBRNALoopSecondaryStructure,
    DBLigandKineticsProfile,
)


class RiboswitchKineticsRepository:
    """Repository handling CRUD operations for riboswitch circuits, secondary structures, and kinetic profiles."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_circuit(
        self,
        circuit_name: str,
        target_ligand: str,
        rna_sequence: str,
        aptamer_class: str = "SAM-I",
        expression_platform_type: str = "Rho-Independent Terminator",
        dynamic_range_fold: float = 8.5,
        switching_free_energy_delta_g: float = -14.2,
        metadata_json: Optional[Dict[str, Any]] = None,
        project_id: Optional[uuid.UUID] = None,
    ) -> DBRiboswitchCircuit:
        """Create a new riboswitch kinetic switch circuit."""
        circuit = DBRiboswitchCircuit(
            id=uuid.uuid4(),
            project_id=project_id,
            circuit_name=circuit_name,
            target_ligand=target_ligand,
            rna_sequence=rna_sequence,
            aptamer_class=aptamer_class,
            expression_platform_type=expression_platform_type,
            dynamic_range_fold=dynamic_range_fold,
            switching_free_energy_delta_g=switching_free_energy_delta_g,
            metadata_json=metadata_json or {},
        )
        self.session.add(circuit)
        await self.session.commit()
        await self.session.refresh(circuit)
        return circuit

    async def get_circuit(self, circuit_id: uuid.UUID) -> Optional[DBRiboswitchCircuit]:
        """Get riboswitch circuit with secondary structures and kinetic profiles."""
        stmt = (
            select(DBRiboswitchCircuit)
            .options(
                selectinload(DBRiboswitchCircuit.secondary_structures),
                selectinload(DBRiboswitchCircuit.ligand_kinetics),
            )
            .where(DBRiboswitchCircuit.id == circuit_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_circuits(self, limit: int = 50, offset: int = 0) -> List[DBRiboswitchCircuit]:
        """List all riboswitch circuits."""
        stmt = (
            select(DBRiboswitchCircuit)
            .order_by(desc(DBRiboswitchCircuit.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_secondary_structure(
        self,
        circuit_id: uuid.UUID,
        state_name: str,
        dot_bracket_notation: str,
        minimum_free_energy_mfe: float,
        ensemble_defect_percent: float = 4.2,
        pseudoknot_present: str = "NO",
    ) -> DBRNALoopSecondaryStructure:
        """Add an RNA secondary structure conformation."""
        struct = DBRNALoopSecondaryStructure(
            id=uuid.uuid4(),
            circuit_id=circuit_id,
            state_name=state_name,
            dot_bracket_notation=dot_bracket_notation,
            minimum_free_energy_mfe=minimum_free_energy_mfe,
            ensemble_defect_percent=ensemble_defect_percent,
            pseudoknot_present=pseudoknot_present,
        )
        self.session.add(struct)
        await self.session.commit()
        await self.session.refresh(struct)
        return struct

    async def add_kinetics_profile(
        self,
        circuit_id: uuid.UUID,
        association_rate_k_on: float,
        dissociation_rate_k_off: float,
        equilibrium_dissociation_constant_kd_nm: float,
        cotranscriptional_folding_window_nt: int = 45,
    ) -> DBLigandKineticsProfile:
        """Add a ligand binding kinetics profile."""
        profile = DBLigandKineticsProfile(
            id=uuid.uuid4(),
            circuit_id=circuit_id,
            association_rate_k_on=association_rate_k_on,
            dissociation_rate_k_off=dissociation_rate_k_off,
            equilibrium_dissociation_constant_kd_nm=equilibrium_dissociation_constant_kd_nm,
            cotranscriptional_folding_window_nt=cotranscriptional_folding_window_nt,
        )
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile
