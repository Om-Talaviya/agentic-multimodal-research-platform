"""Repository for Diffusion-Based 3D Complex Conformation Generation."""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.diffusion_conformation import (
    DBDiffusionComplexJob,
    DBDiffusionPocketConformation,
    DBEquivariantDockingPose,
)


class DiffusionConformationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_job(
        self,
        protein_pdb_id: str,
        ligand_smiles: str,
        diffusion_model_variant: str = "DiffDock_SE3",
        num_diffusion_timesteps: int = 1000,
        sampling_temperature: float = 1.0,
        total_conformations_generated: int = 5,
        best_confidence_score: float = 0.942,
        status: str = "COMPLETED",
        job_metadata_json: Optional[Dict[str, Any]] = None,
    ) -> DBDiffusionComplexJob:
        job = DBDiffusionComplexJob(
            protein_pdb_id=protein_pdb_id,
            ligand_smiles=ligand_smiles,
            diffusion_model_variant=diffusion_model_variant,
            num_diffusion_timesteps=num_diffusion_timesteps,
            sampling_temperature=sampling_temperature,
            total_conformations_generated=total_conformations_generated,
            best_confidence_score=best_confidence_score,
            status=status,
            job_metadata_json=job_metadata_json or {},
        )
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def add_pocket_conformation(
        self,
        job_id: str,
        conformation_rank: int = 1,
        pocket_center_x: float = 12.45,
        pocket_center_y: float = -4.20,
        pocket_center_z: float = 28.15,
        pocket_volume_angstrom3: float = 485.6,
        cavity_druggability_score: float = 0.88,
        clash_penalty_score: float = 0.04,
    ) -> DBDiffusionPocketConformation:
        conf = DBDiffusionPocketConformation(
            job_id=job_id,
            conformation_rank=conformation_rank,
            pocket_center_x=pocket_center_x,
            pocket_center_y=pocket_center_y,
            pocket_center_z=pocket_center_z,
            pocket_volume_angstrom3=pocket_volume_angstrom3,
            cavity_druggability_score=cavity_druggability_score,
            clash_penalty_score=clash_penalty_score,
        )
        self.session.add(conf)
        await self.session.commit()
        await self.session.refresh(conf)
        return conf

    async def add_docking_pose(
        self,
        job_id: str,
        pose_rank: int = 1,
        rmsd_to_centroid_angstrom: float = 0.82,
        vina_affinity_score: float = -9.45,
        se3_confidence_score: float = 0.942,
        num_h_bonds: int = 4,
        contact_surface_area_angstrom2: float = 320.5,
        ligand_coordinates_pdb: str = "",
    ) -> DBEquivariantDockingPose:
        pose = DBEquivariantDockingPose(
            job_id=job_id,
            pose_rank=pose_rank,
            rmsd_to_centroid_angstrom=rmsd_to_centroid_angstrom,
            vina_affinity_score=vina_affinity_score,
            se3_confidence_score=se3_confidence_score,
            num_h_bonds=num_h_bonds,
            contact_surface_area_angstrom2=contact_surface_area_angstrom2,
            ligand_coordinates_pdb=ligand_coordinates_pdb,
        )
        self.session.add(pose)
        await self.session.commit()
        await self.session.refresh(pose)
        return pose

    async def get_job(self, job_id: str) -> Optional[DBDiffusionComplexJob]:
        stmt = (
            select(DBDiffusionComplexJob)
            .where(DBDiffusionComplexJob.id == job_id)
            .options(
                selectinload(DBDiffusionComplexJob.pocket_conformations),
                selectinload(DBDiffusionComplexJob.docking_poses),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_jobs(self, limit: int = 50) -> List[DBDiffusionComplexJob]:
        stmt = (
            select(DBDiffusionComplexJob)
            .options(
                selectinload(DBDiffusionComplexJob.pocket_conformations),
                selectinload(DBDiffusionComplexJob.docking_poses),
            )
            .order_by(desc(DBDiffusionComplexJob.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
