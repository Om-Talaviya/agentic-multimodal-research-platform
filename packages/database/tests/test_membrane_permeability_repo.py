"""Tests for MembranePermeabilityRepository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.membrane_permeability_repo import MembranePermeabilityRepository


@pytest_asyncio.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_membrane_permeability_repo_lifecycle(async_db: AsyncSession):
    repo = MembranePermeabilityRepository(async_db)

    study = await repo.create_study(
        molecule_name="Propranolol",
        smiles="CC(C)NCC(O)COC1=CC=CC2=CC=CC=C12",
        molecular_weight=259.34,
        logp=2.6,
        tpsa=41.49,
        papp_cm_per_s=18.5e-6,
        permeability_class="High",
    )
    assert study.id is not None

    await repo.add_diffusivity_record(
        study_id=study.id,
        bilayer_depth_angstrom=15.0,
        free_energy_barrier_kcal_mol=2.4,
        local_diffusion_coefficient=1.2e-5,
    )

    await repo.add_qsar_profile(
        study_id=study.id,
        h_bond_donors=2,
        h_bond_acceptors=3,
        rotatable_bonds=6,
        predicted_pampa_score=0.91,
        is_blood_brain_barrier_permeable=True,
    )

    loaded = await repo.get_study_with_details(study.id)
    assert loaded is not None
    assert len(loaded.diffusivity_records) == 1
    assert len(loaded.qsar_profiles) == 1
    assert loaded.qsar_profiles[0].is_blood_brain_barrier_permeable is True
