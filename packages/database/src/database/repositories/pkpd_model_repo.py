"""Repository for PK/PD Simulation & Modeling data access (Phase 99)."""

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.models.pkpd_model import (
    DBPkPdSimulation,
    DBTissueConcentration,
    DBPharmacodynamicEffect,
)


class PkPdSimulationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_simulation(
        self,
        workspace_id: uuid.UUID,
        drug_name: str,
        route_of_administration: str,
        dose_mg: float,
        dosing_interval_hours: float,
        cmax_ug_ml: float,
        tmax_hours: float,
        auc_inf_ug_hr_ml: float,
        elimination_half_life_hours: float,
        clearance_l_per_hr: float,
        volume_distribution_l: float,
        therapeutic_window_compliance: str = "OPTIMAL",
        simulation_metadata: Optional[Dict[str, Any]] = None,
    ) -> DBPkPdSimulation:
        sim = DBPkPdSimulation(
            workspace_id=workspace_id,
            drug_name=drug_name,
            route_of_administration=route_of_administration,
            dose_mg=dose_mg,
            dosing_interval_hours=dosing_interval_hours,
            cmax_ug_ml=cmax_ug_ml,
            tmax_hours=tmax_hours,
            auc_inf_ug_hr_ml=auc_inf_ug_hr_ml,
            elimination_half_life_hours=elimination_half_life_hours,
            clearance_l_per_hr=clearance_l_per_hr,
            volume_distribution_l=volume_distribution_l,
            therapeutic_window_compliance=therapeutic_window_compliance,
            simulation_metadata=simulation_metadata or {},
        )
        self.session.add(sim)
        await self.session.commit()
        await self.session.refresh(sim)
        return sim

    async def add_tissue_concentration(
        self,
        simulation_id: uuid.UUID,
        tissue_organ: str,
        kp_partition_coefficient: float,
        cmax_tissue_ug_g: float,
        auc_tissue_ug_hr_g: float,
    ) -> DBTissueConcentration:
        tc = DBTissueConcentration(
            simulation_id=simulation_id,
            tissue_organ=tissue_organ,
            kp_partition_coefficient=kp_partition_coefficient,
            cmax_tissue_ug_g=cmax_tissue_ug_g,
            auc_tissue_ug_hr_g=auc_tissue_ug_hr_g,
        )
        self.session.add(tc)
        await self.session.commit()
        await self.session.refresh(tc)
        return tc

    async def add_pd_effect(
        self,
        simulation_id: uuid.UUID,
        biomarker_name: str,
        emax_percent: float,
        ec50_ug_ml: float,
        hill_coefficient: float,
        max_effect_observed: float,
        duration_above_ic90_hours: float = 18.5,
    ) -> DBPharmacodynamicEffect:
        pe = DBPharmacodynamicEffect(
            simulation_id=simulation_id,
            biomarker_name=biomarker_name,
            emax_percent=emax_percent,
            ec50_ug_ml=ec50_ug_ml,
            hill_coefficient=hill_coefficient,
            max_effect_observed=max_effect_observed,
            duration_above_ic90_hours=duration_above_ic90_hours,
        )
        self.session.add(pe)
        await self.session.commit()
        await self.session.refresh(pe)
        return pe

    async def get_simulation(self, simulation_id: uuid.UUID) -> Optional[DBPkPdSimulation]:
        stmt = (
            select(DBPkPdSimulation)
            .options(
                selectinload(DBPkPdSimulation.tissue_concentrations),
                selectinload(DBPkPdSimulation.pd_effects),
            )
            .where(DBPkPdSimulation.id == simulation_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
