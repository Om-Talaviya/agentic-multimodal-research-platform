"""
Tests for MolecularStructureRepository.
"""

import pytest
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from database.connection import Base
from database.models.user import User as DBUser
from database.models.molecular import (
    DBMolecularStructure,
    DBBindingPocket,
    DBDockingPose,
    DBMutationStability,
)
from database.repositories.molecular_repo import MolecularStructureRepository


@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_and_get_structure(async_session: AsyncSession):
    user_id = uuid.uuid4()
    user = DBUser(id=user_id, username="test_bio", email="bio@alpha.org", password_hash="hash")
    async_session.add(user)
    await async_session.commit()

    repo = MolecularStructureRepository(async_session)

    structure = await repo.create_structure(
        user_id=user_id,
        uniprot_id="Q9BYF1",
        gene_name="PCSK9",
        sequence="MGTVSSRRSWWPLPLLL",
        pdb_coordinate_data="HEADER PCSK9 MODEL\nATOM 1 CA ALA A 1 0.0 0.0 0.0 1.00 92.5\nEND\n",
        mean_plddt_score=91.4,
        structure_source="AlphaFold3",
        secondary_structure_summary={"alpha_helix_pct": 42.5, "beta_sheet_pct": 18.2},
    )

    assert structure.id is not None
    assert structure.gene_name == "PCSK9"
    assert structure.uniprot_id == "Q9BYF1"
    assert structure.mean_plddt_score == 91.4

    fetched = await repo.get_structure(structure.id)
    assert fetched is not None
    assert fetched.gene_name == "PCSK9"
    assert fetched.structure_source == "AlphaFold3"


@pytest.mark.asyncio
async def test_binding_pockets_and_docking(async_session: AsyncSession):
    user_id = uuid.uuid4()
    user = DBUser(id=user_id, username="test_bio2", email="bio2@alpha.org", password_hash="hash")
    async_session.add(user)
    await async_session.commit()

    repo = MolecularStructureRepository(async_session)

    structure = await repo.create_structure(
        user_id=user_id,
        uniprot_id="P00533",
        gene_name="EGFR",
        sequence="LLEGEKIR",
        pdb_coordinate_data="HEADER EGFR\nEND",
        mean_plddt_score=87.2,
    )

    # Add pocket
    pocket = await repo.add_binding_pocket(
        structure_id=structure.id,
        pocket_index=1,
        druggability_score=0.92,
        volume_cubic_angstrom=850.5,
        surface_area_angstrom2=480.0,
        key_residues_json=["GLU762", "MET793", "THR790"],
        center_coordinates_json={"x": 12.4, "y": 3.2, "z": -14.8},
    )
    assert pocket.id is not None
    assert pocket.druggability_score == 0.92

    # Add docking pose
    pose = await repo.add_docking_pose(
        structure_id=structure.id,
        pocket_id=pocket.id,
        ligand_name="Osimertinib",
        binding_affinity_kcal_mol=-10.8,
        rmsd_angstrom=1.1,
        hydrogen_bonds_count=3,
        pi_stacking_interactions=2,
    )
    assert pose.id is not None
    assert pose.binding_affinity_kcal_mol == -10.8

    # Query structure with relations
    fetched = await repo.get_structure(structure.id)
    assert fetched is not None
    assert len(fetched.binding_pockets) == 1
    assert len(fetched.docking_poses) == 1
    assert fetched.docking_poses[0].ligand_name == "Osimertinib"


@pytest.mark.asyncio
async def test_mutation_stability(async_session: AsyncSession):
    user_id = uuid.uuid4()
    user = DBUser(id=user_id, username="test_bio3", email="bio3@alpha.org", password_hash="hash")
    async_session.add(user)
    await async_session.commit()

    repo = MolecularStructureRepository(async_session)

    structure = await repo.create_structure(
        user_id=user_id,
        uniprot_id="P04637",
        gene_name="TP53",
        sequence="MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGP",
        pdb_coordinate_data="HEADER p53\nEND",
        mean_plddt_score=88.0,
    )

    mutation = await repo.add_mutation_stability(
        structure_id=structure.id,
        wildtype_residue="R",
        position=248,
        mutant_residue="W",
        delta_delta_g_kcal_mol=3.4,
        stability_verdict="destabilizing",
        pathogenicity_score=0.92,
    )
    assert mutation.id is not None
    assert mutation.delta_delta_g_kcal_mol == 3.4
    assert mutation.stability_verdict == "destabilizing"

    fetched = await repo.get_structure(structure.id)
    assert fetched is not None
    assert len(fetched.mutations) == 1
    assert fetched.mutations[0].mutant_residue == "W"
