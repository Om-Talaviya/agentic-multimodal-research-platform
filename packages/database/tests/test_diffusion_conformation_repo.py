"""Tests for DiffusionConformationRepository."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.diffusion_conformation_repo import DiffusionConformationRepository


@pytest.mark.asyncio
async def test_diffusion_conformation_repo_lifecycle(db_session: AsyncSession):
    repo = DiffusionConformationRepository(db_session)

    # 1. Create Job
    job = await repo.create_job(
        protein_pdb_id="6LU7",
        ligand_smiles="CC(C)CC(C=O)NC(=O)C(CC1=CC=CC=C1)NC(=O)OCC2=CC=CC=C2",
        diffusion_model_variant="DiffDock_SE3",
        num_diffusion_timesteps=1000,
        best_confidence_score=0.955,
    )
    assert job.id is not None
    assert job.protein_pdb_id == "6LU7"
    assert job.best_confidence_score == 0.955

    # 2. Add Pocket Conformation
    pocket = await repo.add_pocket_conformation(
        job_id=job.id,
        conformation_rank=1,
        pocket_center_x=12.5,
        pocket_center_y=-4.0,
        pocket_center_z=28.0,
        pocket_volume_angstrom3=512.4,
        cavity_druggability_score=0.91,
        clash_penalty_score=0.02,
    )
    assert pocket.id is not None
    assert pocket.cavity_druggability_score == 0.91

    # 3. Add Docking Pose
    pose = await repo.add_docking_pose(
        job_id=job.id,
        pose_rank=1,
        rmsd_to_centroid_angstrom=0.68,
        vina_affinity_score=-10.2,
        se3_confidence_score=0.955,
        num_h_bonds=5,
        contact_surface_area_angstrom2=345.0,
        ligand_coordinates_pdb="HETATM...",
    )
    assert pose.id is not None
    assert pose.vina_affinity_score == -10.2

    # 4. Fetch Job
    fetched = await repo.get_job(job.id)
    assert fetched is not None
    assert len(fetched.pocket_conformations) == 1
    assert len(fetched.docking_poses) == 1

    # 5. List Jobs
    jobs = await repo.list_jobs()
    assert len(jobs) >= 1
