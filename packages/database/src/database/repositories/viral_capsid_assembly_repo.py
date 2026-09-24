"""Repository for AAV Viral Capsid Self-Assembly (Phase 151)."""

import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.viral_capsid_assembly import (
    DBViralCapsidAssemblyStudy,
    DBCapsomerInterfaceEnergy,
    DBCapsidThermodynamicTrajectory,
)


class CapsidAssemblyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_study(
        self,
        serotype_name: str,
        triangulation_number: str,
        vp_stoichiometry_ratio: str,
        assembly_yield_percent: float,
        gibbs_free_energy_kcal_mol: float,
        critical_nucleus_size: int,
        full_empty_capsid_ratio: float,
    ) -> DBViralCapsidAssemblyStudy:
        study = DBViralCapsidAssemblyStudy(
            id=uuid.uuid4(),
            serotype_name=serotype_name,
            triangulation_number=triangulation_number,
            vp_stoichiometry_ratio=vp_stoichiometry_ratio,
            assembly_yield_percent=assembly_yield_percent,
            gibbs_free_energy_kcal_mol=gibbs_free_energy_kcal_mol,
            critical_nucleus_size=critical_nucleus_size,
            full_empty_capsid_ratio=full_empty_capsid_ratio,
        )
        self.db.add(study)
        await self.db.commit()
        await self.db.refresh(study)
        return study

    async def add_interface(
        self,
        study_id: uuid.UUID,
        symmetry_axis: str,
        delta_g_binding_kcal_mol: float,
        buried_surface_area_a2: float,
        hydrogen_bonds_count: int,
        salt_bridges_count: int,
    ) -> DBCapsomerInterfaceEnergy:
        rec = DBCapsomerInterfaceEnergy(
            id=uuid.uuid4(),
            study_id=study_id,
            symmetry_axis=symmetry_axis,
            delta_g_binding_kcal_mol=delta_g_binding_kcal_mol,
            buried_surface_area_a2=buried_surface_area_a2,
            hydrogen_bonds_count=hydrogen_bonds_count,
            salt_bridges_count=salt_bridges_count,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def add_trajectory(
        self,
        study_id: uuid.UUID,
        oligomer_size: int,
        forward_rate_k_on: float,
        reverse_rate_k_off: float,
        fraction_assembled: float,
    ) -> DBCapsidThermodynamicTrajectory:
        rec = DBCapsidThermodynamicTrajectory(
            id=uuid.uuid4(),
            study_id=study_id,
            oligomer_size=oligomer_size,
            forward_rate_k_on=forward_rate_k_on,
            reverse_rate_k_off=reverse_rate_k_off,
            fraction_assembled=fraction_assembled,
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec

    async def get_study_with_details(self, study_id: uuid.UUID) -> Optional[DBViralCapsidAssemblyStudy]:
        stmt = (
            select(DBViralCapsidAssemblyStudy)
            .where(DBViralCapsidAssemblyStudy.id == study_id)
            .options(
                selectinload(DBViralCapsidAssemblyStudy.interfaces),
                selectinload(DBViralCapsidAssemblyStudy.trajectories),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
