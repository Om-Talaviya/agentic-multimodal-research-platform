"""Lineage Repo (Phase 114)."""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database.models.lineage_tracing import DBLineageBarcodeExperiment, DBClonalLineageTrajectory

class LineageTracingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_experiment(self, workspace_id: uuid.UUID, experiment_title: str,
                                barcoding_technology: str, total_unique_clones: int,
                                shannon_entropy_diversity: float,
                                dominant_clone_fraction: float) -> DBLineageBarcodeExperiment:
        exp = DBLineageBarcodeExperiment(
            workspace_id=workspace_id,
            experiment_title=experiment_title,
            barcoding_technology=barcoding_technology,
            total_unique_clones=total_unique_clones,
            shannon_entropy_diversity=shannon_entropy_diversity,
            dominant_clone_fraction=dominant_clone_fraction,
        )
        self.db.add(exp)
        await self.db.commit()
        await self.db.refresh(exp)
        return exp

    async def add_trajectory(self, experiment_id: uuid.UUID, clone_barcode_id: str,
                             initial_frequency: float, post_selection_frequency: float,
                             relative_fitness_coefficient: float,
                             resistance_conferring_driver: str) -> DBClonalLineageTrajectory:
        traj = DBClonalLineageTrajectory(
            experiment_id=experiment_id,
            clone_barcode_id=clone_barcode_id,
            initial_frequency=initial_frequency,
            post_selection_frequency=post_selection_frequency,
            relative_fitness_coefficient=relative_fitness_coefficient,
            resistance_conferring_driver=resistance_conferring_driver,
        )
        self.db.add(traj)
        await self.db.commit()
        await self.db.refresh(traj)
        return traj

    async def get_experiment(self, experiment_id: uuid.UUID) -> Optional[DBLineageBarcodeExperiment]:
        res = await self.db.execute(select(DBLineageBarcodeExperiment).where(DBLineageBarcodeExperiment.id == experiment_id))
        return res.scalar_one_or_none()
