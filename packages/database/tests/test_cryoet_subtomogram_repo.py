"""Tests for Cryo-ET Subtomogram Averaging repository."""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.repositories.cryoet_subtomogram_repo import CryoETSubtomogramRepository


@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_create_and_get_cryoet_dataset(async_session: AsyncSession):
    repo = CryoETSubtomogramRepository(async_session)

    dataset = await repo.create_dataset(
        sample_name="Ribosome In-Situ",
        specimen_organism="S. cerevisiae",
        cellular_compartment="CYTOSOL",
        tilt_angle_min=-60.0,
        tilt_angle_max=60.0,
        total_tilt_images=41,
        pixel_size_angstrom=1.35,
        nominal_defocus_um=-2.5,
    )

    assert dataset.id is not None
    assert dataset.sample_name == "Ribosome In-Situ"

    fetched = await repo.get_dataset(dataset.id)
    assert fetched is not None
    assert fetched.specimen_organism == "S. cerevisiae"


@pytest.mark.asyncio
async def test_add_particles_and_refinement(async_session: AsyncSession):
    repo = CryoETSubtomogramRepository(async_session)

    dataset = await repo.create_dataset(
        sample_name="NPC Cytoplasmic Ring",
        specimen_organism="H. sapiens",
        cellular_compartment="NUCLEAR_PORE",
    )

    particles_data = [
        {
            "particle_index": 1,
            "coord_x": 100.5,
            "coord_y": 200.5,
            "coord_z": 50.0,
            "euler_phi": 45.0,
            "euler_theta": 30.0,
            "euler_psi": 90.0,
            "cross_correlation_score": 0.82,
            "class_assignment": "CLASS_1",
        }
    ]

    particles = await repo.add_particles(dataset.id, particles_data)
    assert len(particles) == 1

    refinement = await repo.add_refinement(
        dataset_id=dataset.id,
        class_name="Consensus Class 1",
        particles_averaged_count=100,
        estimated_resolution_angstrom=4.2,
        fsc_0143_spatial_frequency=0.238,
        b_factor_sharpening=-120.0,
        fsc_curve_json=[{"spatial_frequency": 0.238, "fsc_correlation": 0.143}],
    )

    assert refinement.id is not None
    assert refinement.estimated_resolution_angstrom == 4.2

    fetched_particles = await repo.get_particles_by_dataset(dataset.id)
    assert len(fetched_particles) == 1

    fetched_refs = await repo.get_refinements_by_dataset(dataset.id)
    assert len(fetched_refs) == 1
