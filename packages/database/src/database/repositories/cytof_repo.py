"""
Phase 109: High-Dimensional CyTOF Phenotyping Repository.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
import uuid

from database.models.cytof import (
    DBCyTOFExperiment,
    DBCyTOFMetalChannel,
    DBSingleCellCyTOFCluster,
)

class CyTOFRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_experiment(
        self,
        experiment_name: str,
        tissue_type: str = "PBMC",
        cell_count: int = 5000,
        panel_size: int = 35,
        cofactor: float = 5.0,
        is_compensated: bool = True,
        project_id: Optional[str] = None,
    ) -> DBCyTOFExperiment:
        exp = DBCyTOFExperiment(
            id=uuid.uuid4(),
            project_id=project_id,
            experiment_name=experiment_name,
            tissue_type=tissue_type,
            cell_count=cell_count,
            panel_size=panel_size,
            cofactor=cofactor,
            is_compensated=is_compensated,
        )
        self.session.add(exp)
        await self.session.commit()
        await self.session.refresh(exp)
        return exp

    async def get_experiment(self, experiment_id: uuid.UUID) -> Optional[DBCyTOFExperiment]:
        stmt = (
            select(DBCyTOFExperiment)
            .options(selectinload(DBCyTOFExperiment.channels), selectinload(DBCyTOFExperiment.clusters))
            .where(DBCyTOFExperiment.id == experiment_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_metal_channel(
        self,
        experiment_id: uuid.UUID,
        channel_name: str,
        metal_isotope: str,
        target_marker: str,
        mean_intensity: float = 0.0,
        signal_to_noise: float = 10.0,
        spillover_matrix: Optional[Dict[str, Any]] = None,
    ) -> DBCyTOFMetalChannel:
        channel = DBCyTOFMetalChannel(
            id=uuid.uuid4(),
            experiment_id=experiment_id,
            channel_name=channel_name,
            metal_isotope=metal_isotope,
            target_marker=target_marker,
            mean_intensity=mean_intensity,
            signal_to_noise=signal_to_noise,
            spillover_matrix=spillover_matrix or {},
        )
        self.session.add(channel)
        await self.session.commit()
        await self.session.refresh(channel)
        return channel

    async def add_cluster(
        self,
        experiment_id: uuid.UUID,
        cluster_id: int,
        cluster_name: str,
        cell_frequency: float,
        marker_enrichment_profile: Dict[str, Any],
        phenograph_k: int = 30,
        tsne_coordinates_2d: Optional[List[Dict[str, Any]]] = None,
    ) -> DBSingleCellCyTOFCluster:
        cluster = DBSingleCellCyTOFCluster(
            id=uuid.uuid4(),
            experiment_id=experiment_id,
            cluster_id=cluster_id,
            cluster_name=cluster_name,
            cell_frequency=cell_frequency,
            marker_enrichment_profile=marker_enrichment_profile,
            phenograph_k=phenograph_k,
            tsne_coordinates_2d=tsne_coordinates_2d or [],
        )
        self.session.add(cluster)
        await self.session.commit()
        await self.session.refresh(cluster)
        return cluster

    async def list_channels(self, experiment_id: uuid.UUID) -> List[DBCyTOFMetalChannel]:
        stmt = select(DBCyTOFMetalChannel).where(DBCyTOFMetalChannel.experiment_id == experiment_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_clusters(self, experiment_id: uuid.UUID) -> List[DBSingleCellCyTOFCluster]:
        stmt = select(DBSingleCellCyTOFCluster).where(DBSingleCellCyTOFCluster.experiment_id == experiment_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
