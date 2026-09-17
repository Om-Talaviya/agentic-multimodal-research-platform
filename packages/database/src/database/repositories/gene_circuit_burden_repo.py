from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from database.models.gene_circuit_burden import (
    DBCircuitBurdenSimulation,
    DBHostCapacityModel,
)

class GeneCircuitBurdenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_simulation(
        self,
        circuit_name: str,
        host_organism: str = "E. coli K-12",
        promoter_strength_rpum: float = 1250.0,
        ribosome_allocation_pct: float = 18.5,
        growth_rate_penalty_pct: float = 14.2,
        evolutionary_half_life_generations: float = 42.0,
        circuit_failure_mode: str = "IS Insertion",
        properties: Optional[Dict[str, Any]] = None,
    ) -> DBCircuitBurdenSimulation:
        sim = DBCircuitBurdenSimulation(
            circuit_name=circuit_name,
            host_organism=host_organism,
            promoter_strength_rpum=promoter_strength_rpum,
            ribosome_allocation_pct=ribosome_allocation_pct,
            growth_rate_penalty_pct=growth_rate_penalty_pct,
            evolutionary_half_life_generations=evolutionary_half_life_generations,
            circuit_failure_mode=circuit_failure_mode,
            properties=properties or {},
        )
        self.session.add(sim)
        await self.session.commit()
        await self.session.refresh(sim)
        return sim

    async def add_host_capacity_model(
        self,
        simulation_id: str,
        free_ribosome_pool_fraction: float = 0.72,
        atp_drain_flux_mmol_gdw_h: float = 2.8,
        chaperone_load_index: float = 0.35,
        metabolic_burden_status: str = "BALANCED",
    ) -> DBHostCapacityModel:
        model = DBHostCapacityModel(
            simulation_id=simulation_id,
            free_ribosome_pool_fraction=free_ribosome_pool_fraction,
            atp_drain_flux_mmol_gdw_h=atp_drain_flux_mmol_gdw_h,
            chaperone_load_index=chaperone_load_index,
            metabolic_burden_status=metabolic_burden_status,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def get_simulation_by_id(self, simulation_id: str) -> Optional[DBCircuitBurdenSimulation]:
        stmt = (
            select(DBCircuitBurdenSimulation)
            .options(selectinload(DBCircuitBurdenSimulation.capacity_models))
            .where(DBCircuitBurdenSimulation.id == simulation_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_simulations(self, limit: int = 50) -> List[DBCircuitBurdenSimulation]:
        stmt = (
            select(DBCircuitBurdenSimulation)
            .options(selectinload(DBCircuitBurdenSimulation.capacity_models))
            .order_by(DBCircuitBurdenSimulation.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
