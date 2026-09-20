"""
Repository for Phase 108: Organ-on-a-Chip Fluidic Dynamics.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
import uuid

from database.models.organ_chip import DBOrganOnChipSimulation, DBMicrofluidicChannel, DBShearStressProfile

class OrganChipRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_simulation(
        self,
        chip_name: str,
        user_id: Optional[uuid.UUID] = None,
        organ_type: str = "BLOOD_BRAIN_BARRIER",
        fluid_viscosity_cp: float = 1.0,
        perfusion_flow_rate_ul_min: float = 30.0,
        shear_stress_dyn_cm2: float = 5.2,
        endothelial_barrier_integrity_teer: float = 1250.0,
        metadata_json: Optional[Dict[str, Any]] = None,
    ) -> DBOrganOnChipSimulation:
        sim = DBOrganOnChipSimulation(
            id=uuid.uuid4(),
            user_id=user_id,
            chip_name=chip_name,
            organ_type=organ_type,
            fluid_viscosity_cp=fluid_viscosity_cp,
            perfusion_flow_rate_ul_min=perfusion_flow_rate_ul_min,
            shear_stress_dyn_cm2=shear_stress_dyn_cm2,
            endothelial_barrier_integrity_teer=endothelial_barrier_integrity_teer,
            metadata_json=metadata_json or {},
            status="COMPLETED"
        )
        self.session.add(sim)
        await self.session.commit()
        await self.session.refresh(sim)
        return sim

    async def get_simulation(self, simulation_id: uuid.UUID) -> Optional[DBOrganOnChipSimulation]:
        stmt = (
            select(DBOrganOnChipSimulation)
            .options(selectinload(DBOrganOnChipSimulation.channels), selectinload(DBOrganOnChipSimulation.shear_profiles))
            .where(DBOrganOnChipSimulation.id == simulation_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_simulations(self, limit: int = 50, offset: int = 0) -> List[DBOrganOnChipSimulation]:
        stmt = (
            select(DBOrganOnChipSimulation)
            .order_by(desc(DBOrganOnChipSimulation.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_channels(
        self,
        simulation_id: uuid.UUID,
        channels_data: List[Dict[str, Any]]
    ) -> List[DBMicrofluidicChannel]:
        entities = []
        for ch in channels_data:
            entity = DBMicrofluidicChannel(
                id=uuid.uuid4(),
                simulation_id=simulation_id,
                channel_name=ch["channel_name"],
                width_um=ch.get("width_um", 400.0),
                height_um=ch.get("height_um", 100.0),
                length_mm=ch.get("length_mm", 20.0),
                flow_velocity_mm_s=ch.get("flow_velocity_mm_s", 2.5),
                reynolds_number=ch.get("reynolds_number", 0.08)
            )
            entities.append(entity)
            self.session.add(entity)
        await self.session.commit()
        return entities

    async def add_shear_profiles(
        self,
        simulation_id: uuid.UUID,
        profiles_data: List[Dict[str, Any]]
    ) -> List[DBShearStressProfile]:
        entities = []
        for p in profiles_data:
            entity = DBShearStressProfile(
                id=uuid.uuid4(),
                simulation_id=simulation_id,
                axial_position_mm=p["axial_position_mm"],
                wall_shear_stress=p.get("wall_shear_stress", 5.0),
                drug_permeation_pct=p.get("drug_permeation_pct", 10.0),
                tight_junction_expression=p.get("tight_junction_expression", 95.0)
            )
            entities.append(entity)
            self.session.add(entity)
        await self.session.commit()
        return entities
