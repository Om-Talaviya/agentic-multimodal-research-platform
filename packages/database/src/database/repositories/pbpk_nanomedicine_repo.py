"""
Repository for Nanomedicine PBPK Simulator (Phase 60).
"""
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.pbpk_nanomedicine import (
    DBNanomedicinePBPKSimulation,
    DBOrganCompartmentPK,
    DBNanoparticleClearancePathway,
)


class NanomedicinePBPKRepository:
    """Handles CRUD operations for nanomedicine PBPK simulation experiments."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_simulation(
        self,
        formulation_name: str,
        carrier_type: str = "Lipid Nanoparticle (LNP)",
        hydrodynamic_diameter_nm: float = 85.0,
        zeta_potential_mv: float = -4.2,
        pegylation_density_pct: float = 1.5,
        dose_mg_kg: float = 1.0,
        tumor_epr_permeability_index: float = 0.82,
        metadata_info: Optional[Dict[str, Any]] = None,
    ) -> DBNanomedicinePBPKSimulation:
        sim = DBNanomedicinePBPKSimulation(
            id=str(uuid.uuid4()),
            formulation_name=formulation_name,
            carrier_type=carrier_type,
            hydrodynamic_diameter_nm=hydrodynamic_diameter_nm,
            zeta_potential_mv=zeta_potential_mv,
            pegylation_density_pct=pegylation_density_pct,
            dose_mg_kg=dose_mg_kg,
            tumor_epr_permeability_index=tumor_epr_permeability_index,
            metadata_info=metadata_info or {},
        )
        self.session.add(sim)
        await self.session.flush()
        await self.session.commit()
        return sim

    async def add_compartments_and_clearance(
        self,
        simulation_id: str,
        compartments_data: List[Dict[str, Any]],
        clearance_data: List[Dict[str, Any]],
    ) -> DBNanomedicinePBPKSimulation:
        for c in compartments_data:
            comp = DBOrganCompartmentPK(
                id=str(uuid.uuid4()),
                simulation_id=simulation_id,
                organ_name=c["organ_name"],
                auc_ug_h_ml=c["auc_ug_h_ml"],
                cmax_ug_ml=c["cmax_ug_ml"],
                tmax_hours=c.get("tmax_hours", 2.0),
                organ_to_plasma_ratio=c.get("organ_to_plasma_ratio", 1.0),
                fraction_of_dose_pct=c.get("fraction_of_dose_pct", 10.0),
            )
            self.session.add(comp)

        for cl in clearance_data:
            path = DBNanoparticleClearancePathway(
                id=str(uuid.uuid4()),
                simulation_id=simulation_id,
                pathway_name=cl["pathway_name"],
                clearance_fraction_pct=cl["clearance_fraction_pct"],
                half_life_hours=cl["half_life_hours"],
            )
            self.session.add(path)

        await self.session.flush()
        await self.session.commit()
        return await self.get_simulation(simulation_id)

    async def get_simulation(self, simulation_id: str) -> Optional[DBNanomedicinePBPKSimulation]:
        self.session.expire_all()
        query = (
            select(DBNanomedicinePBPKSimulation)
            .options(
                selectinload(DBNanomedicinePBPKSimulation.compartments),
                selectinload(DBNanomedicinePBPKSimulation.clearance_pathways),
            )
            .where(DBNanomedicinePBPKSimulation.id == simulation_id)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list_simulations(self, limit: int = 50) -> List[DBNanomedicinePBPKSimulation]:
        query = (
            select(DBNanomedicinePBPKSimulation)
            .options(selectinload(DBNanomedicinePBPKSimulation.compartments))
            .order_by(desc(DBNanomedicinePBPKSimulation.created_at))
            .limit(limit)
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
