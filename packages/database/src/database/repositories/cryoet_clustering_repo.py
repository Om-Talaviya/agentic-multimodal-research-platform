"""
Repository for Phase 133: Autonomous Cryo-ET Cellular Subtomogram Deep Clustering & In-Situ Macromolecular Structure Solver.
"""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from database.models.cryoet_clustering import (
    DBCryoETSubtomogramStudy,
    DBSubtomogramVolume,
    DBInSituMacromoleculeCluster,
)


class CryoETClusteringRepository:
    """Repository handling CRUD operations for Cryo-ET subtomogram studies, volumes, and clusters."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_study(
        self,
        study_name: str,
        cellular_organism: str,
        tilt_series_count: int = 45,
        total_subtomograms_extracted: int = 12500,
        voxel_size_angstrom: float = 1.35,
        mean_resolution_angstrom: float = 3.2,
        metadata_json: Optional[Dict[str, Any]] = None,
        project_id: Optional[str] = None,
    ) -> DBCryoETSubtomogramStudy:
        """Create a new Cryo-ET subtomogram clustering study."""
        study = DBCryoETSubtomogramStudy(
            id=uuid.uuid4(),
            project_id=project_id,
            study_name=study_name,
            cellular_organism=cellular_organism,
            tilt_series_count=tilt_series_count,
            total_subtomograms_extracted=total_subtomograms_extracted,
            voxel_size_angstrom=voxel_size_angstrom,
            mean_resolution_angstrom=mean_resolution_angstrom,
            metadata_json=metadata_json or {},
        )
        self.session.add(study)
        await self.session.commit()
        await self.session.refresh(study)
        return study

    async def get_study(self, study_id: uuid.UUID) -> Optional[DBCryoETSubtomogramStudy]:
        """Get study with associated volumes and clusters."""
        stmt = (
            select(DBCryoETSubtomogramStudy)
            .options(
                selectinload(DBCryoETSubtomogramStudy.volumes),
                selectinload(DBCryoETSubtomogramStudy.clusters),
            )
            .where(DBCryoETSubtomogramStudy.id == study_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_studies(self, limit: int = 50, offset: int = 0) -> List[DBCryoETSubtomogramStudy]:
        """List all Cryo-ET subtomogram studies."""
        stmt = (
            select(DBCryoETSubtomogramStudy)
            .order_by(desc(DBCryoETSubtomogramStudy.created_at))
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_volume(
        self,
        study_id: uuid.UUID,
        volume_tag: str,
        tomogram_id: str,
        coord_x: float,
        coord_y: float,
        coord_z: float,
        signal_to_noise_ratio: float = 1.85,
        cross_correlation_score: float = 0.82,
        assigned_cluster: Optional[str] = None,
    ) -> DBSubtomogramVolume:
        """Add an extracted subtomogram volume point."""
        vol = DBSubtomogramVolume(
            id=uuid.uuid4(),
            study_id=study_id,
            volume_tag=volume_tag,
            tomogram_id=tomogram_id,
            coord_x=coord_x,
            coord_y=coord_y,
            coord_z=coord_z,
            signal_to_noise_ratio=signal_to_noise_ratio,
            cross_correlation_score=cross_correlation_score,
            assigned_cluster=assigned_cluster,
        )
        self.session.add(vol)
        await self.session.commit()
        await self.session.refresh(vol)
        return vol

    async def add_cluster(
        self,
        study_id: uuid.UUID,
        cluster_label: str,
        macromolecule_identity: str,
        particle_count: int = 1200,
        fsc_resolution_angstrom: float = 3.4,
        b_factor_sharpening: float = -85.0,
        conformational_state: str = "Rotational Ground State",
    ) -> DBInSituMacromoleculeCluster:
        """Add an identified in-situ macromolecular cluster."""
        cluster = DBInSituMacromoleculeCluster(
            id=uuid.uuid4(),
            study_id=study_id,
            cluster_label=cluster_label,
            macromolecule_identity=macromolecule_identity,
            particle_count=particle_count,
            fsc_resolution_angstrom=fsc_resolution_angstrom,
            b_factor_sharpening=b_factor_sharpening,
            conformational_state=conformational_state,
        )
        self.session.add(cluster)
        await self.session.commit()
        await self.session.refresh(cluster)
        return cluster
