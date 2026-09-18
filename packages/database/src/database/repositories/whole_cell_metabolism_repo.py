"""Repository for Whole-Cell Metabolic Flux Simulation."""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.whole_cell_metabolism import (
    DBWholeCellModel,
    DBMetabolicFluxState,
    DBKineticSimulationTrace,
)


class WholeCellMetabolicRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_model(
        self,
        organism_name: str,
        genome_scale_model_id: str = "iML1515",
        total_reactions_count: int = 2712,
        total_metabolites_count: int = 1877,
        total_genes_count: int = 1515,
        biomass_objective_reaction: str = "BIOMASS_Ec_iML1515_core_75p37M",
        carbon_source: str = "GLUCOSE",
        optimal_growth_rate_hr1: float = 0.875,
        model_metadata_json: Optional[Dict[str, Any]] = None,
    ) -> DBWholeCellModel:
        model = DBWholeCellModel(
            organism_name=organism_name,
            genome_scale_model_id=genome_scale_model_id,
            total_reactions_count=total_reactions_count,
            total_metabolites_count=total_metabolites_count,
            total_genes_count=total_genes_count,
            biomass_objective_reaction=biomass_objective_reaction,
            carbon_source=carbon_source,
            optimal_growth_rate_hr1=optimal_growth_rate_hr1,
            model_metadata_json=model_metadata_json or {},
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def add_flux_state(
        self,
        model_id: str,
        reaction_id: str,
        reaction_name: str,
        flux_value_mmol_gDW_hr: float = 10.0,
        lower_bound: float = -1000.0,
        upper_bound: float = 1000.0,
        subsystem: str = "GLYCOLYSIS",
        shadow_price: float = 0.0,
    ) -> DBMetabolicFluxState:
        flux = DBMetabolicFluxState(
            model_id=model_id,
            reaction_id=reaction_id,
            reaction_name=reaction_name,
            flux_value_mmol_gDW_hr=flux_value_mmol_gDW_hr,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            subsystem=subsystem,
            shadow_price=shadow_price,
        )
        self.session.add(flux)
        await self.session.commit()
        await self.session.refresh(flux)
        return flux

    async def add_simulation_trace(
        self,
        model_id: str,
        time_point_hours: float = 0.0,
        biomass_concentration_g_L: float = 0.1,
        glucose_concentration_g_L: float = 20.0,
        acetate_concentration_g_L: float = 0.0,
        oxygen_uptake_rate: float = 18.5,
        atp_yield_mol_per_mol_glucose: float = 26.4,
    ) -> DBKineticSimulationTrace:
        trace = DBKineticSimulationTrace(
            model_id=model_id,
            time_point_hours=time_point_hours,
            biomass_concentration_g_L=biomass_concentration_g_L,
            glucose_concentration_g_L=glucose_concentration_g_L,
            acetate_concentration_g_L=acetate_concentration_g_L,
            oxygen_uptake_rate=oxygen_uptake_rate,
            atp_yield_mol_per_mol_glucose=atp_yield_mol_per_mol_glucose,
        )
        self.session.add(trace)
        await self.session.commit()
        await self.session.refresh(trace)
        return trace

    async def get_model(self, model_id: str) -> Optional[DBWholeCellModel]:
        stmt = (
            select(DBWholeCellModel)
            .where(DBWholeCellModel.id == model_id)
            .options(
                selectinload(DBWholeCellModel.flux_states),
                selectinload(DBWholeCellModel.simulation_traces),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_models(self, limit: int = 50) -> List[DBWholeCellModel]:
        stmt = (
            select(DBWholeCellModel)
            .options(
                selectinload(DBWholeCellModel.flux_states),
                selectinload(DBWholeCellModel.simulation_traces),
            )
            .order_by(desc(DBWholeCellModel.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
