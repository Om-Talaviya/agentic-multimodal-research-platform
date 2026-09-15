"""
Tests for MolecularDynamicsRepository.
"""

import pytest
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from database.connection import Base
from database.models.user import User as DBUser
from database.models.molecular_dynamics import (
    DBMolecularDynamicsSimulation,
    DBTrajectoryFrame,
    DBResidueFluctuation,
    DBQuantumChemistryProperty,
)
from database.repositories.molecular_dynamics_repo import MolecularDynamicsRepository


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
async def test_create_and_get_simulation(async_session: AsyncSession):
    user_id = uuid.uuid4()
    user = DBUser(id=user_id, username="test_md", email="md@alpha.org", password_hash="hash")
    async_session.add(user)
    await async_session.commit()

    repo = MolecularDynamicsRepository(async_session)

    sim = await repo.create_simulation(
        user_id=user_id,
        uniprot_id="Q9BYF1",
        system_name="PCSK9 Solvated Box",
        organism="Homo sapiens",
        forcefield="AMBER14SB",
        solvent_model="TIP3P",
        ensemble="NPT",
        total_frames=30,
        timestep_ps=2.0,
        total_duration_ns=100.0,
        temperature_kelvin=300.0,
        pressure_bar=1.013,
        equilibrium_rmsd_angstrom=1.45,
        thermodynamic_data_json={"density_g_cm3": 1.018},
    )

    assert sim.id is not None
    assert sim.system_name == "PCSK9 Solvated Box"
    assert sim.total_duration_ns == 100.0
    assert sim.forcefield == "AMBER14SB"

    fetched = await repo.get_simulation(sim.id)
    assert fetched is not None
    assert fetched.system_name == "PCSK9 Solvated Box"
    assert fetched.equilibrium_rmsd_angstrom == 1.45


@pytest.mark.asyncio
async def test_add_frames_fluctuations_quantum(async_session: AsyncSession):
    user_id = uuid.uuid4()
    user = DBUser(id=user_id, username="test_md2", email="md2@alpha.org", password_hash="hash")
    async_session.add(user)
    await async_session.commit()

    repo = MolecularDynamicsRepository(async_session)

    sim = await repo.create_simulation(
        user_id=user_id,
        uniprot_id="Q9BYF1",
        system_name="PCSK9 Complex",
    )

    frames = await repo.add_trajectory_frames(
        simulation_id=sim.id,
        frames_data=[
            {
                "frame_index": 1,
                "timestamp_ps": 0.0,
                "rmsd_angstrom": 0.0,
                "radius_of_gyration_angstrom": 18.4,
                "potential_energy_kj_mol": -465000.0,
                "kinetic_energy_kj_mol": 98500.0,
                "total_energy_kj_mol": -366500.0,
                "temperature_kelvin": 300.0,
                "frame_pdb_coordinates": "MODEL 1\nATOM 1 CA ALA A 1 0.0 0.0 0.0 1.0 0.0\nENDMDL\n",
            },
            {
                "frame_index": 2,
                "timestamp_ps": 3333.3,
                "rmsd_angstrom": 1.45,
                "radius_of_gyration_angstrom": 18.5,
                "potential_energy_kj_mol": -464800.0,
                "kinetic_energy_kj_mol": 98600.0,
                "total_energy_kj_mol": -366200.0,
                "temperature_kelvin": 300.2,
                "frame_pdb_coordinates": "MODEL 2\nATOM 1 CA ALA A 1 0.1 0.1 0.1 1.0 1.45\nENDMDL\n",
            },
        ],
    )
    assert len(frames) == 2

    fluctuations = await repo.add_residue_fluctuations(
        simulation_id=sim.id,
        fluctuations_data=[
            {
                "residue_number": 1,
                "residue_name": "MET",
                "rmsf_angstrom": 2.15,
                "b_factor_equivalent": 24.5,
                "is_flexible_loop": True,
                "secondary_structure_type": "loop",
            },
            {
                "residue_number": 2,
                "residue_name": "LEU",
                "rmsf_angstrom": 0.65,
                "b_factor_equivalent": 12.1,
                "is_flexible_loop": False,
                "secondary_structure_type": "helix",
            },
        ],
    )
    assert len(fluctuations) == 2

    quantum = await repo.set_quantum_properties(
        simulation_id=sim.id,
        dft_method="B3LYP/6-31G*",
        homo_energy_ev=-6.42,
        lumo_energy_ev=-2.15,
        bandgap_energy_ev=4.27,
        dipole_moment_debye=3.84,
        polarizability_angstrom3=32.4,
        total_scf_energy_hartree=-1845.2918,
    )
    assert quantum.id is not None
    assert quantum.bandgap_energy_ev == 4.27

    detailed = await repo.get_simulation(sim.id)
    assert len(detailed.trajectory_frames) == 2
    assert len(detailed.residue_fluctuations) == 2
    assert detailed.quantum_properties is not None
    assert detailed.quantum_properties.bandgap_energy_ev == 4.27
