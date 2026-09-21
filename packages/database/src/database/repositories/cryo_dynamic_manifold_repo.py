"""Cryo Manifold Repo (Phase 117)."""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.cryo_dynamic_manifold import DBCryoManifoldDataset, DBConformationalManifoldState

class CryoManifoldRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_dataset(self, workspace_id: uuid.UUID, target_complex_name: str,
                             latent_dimensions: int, total_particles_aligned: int,
                             manifold_energy_barrier_kcal: float) -> DBCryoManifoldDataset:
        d = DBCryoManifoldDataset(
            workspace_id=workspace_id,
            target_complex_name=target_complex_name,
            latent_dimensions=latent_dimensions,
            total_particles_aligned=total_particles_aligned,
            manifold_energy_barrier_kcal=manifold_energy_barrier_kcal,
        )
        self.db.add(d)
        await self.db.commit()
        await self.db.refresh(d)
        return d

    async def add_state(self, dataset_id: uuid.UUID, state_label: str,
                        rmsd_from_ground_state: float, relative_population_percentage: float,
                        free_energy_delta_kcal: float) -> DBConformationalManifoldState:
        s = DBConformationalManifoldState(
            dataset_id=dataset_id,
            state_label=state_label,
            rmsd_from_ground_state=rmsd_from_ground_state,
            relative_population_percentage=relative_population_percentage,
            free_energy_delta_kcal=free_energy_delta_kcal,
        )
        self.db.add(s)
        await self.db.commit()
        await self.db.refresh(s)
        return s

    async def get_dataset(self, dataset_id: uuid.UUID) -> Optional[DBCryoManifoldDataset]:
        res = await self.db.execute(select(DBCryoManifoldDataset).where(DBCryoManifoldDataset.id == dataset_id))
        return res.scalar_one_or_none()
