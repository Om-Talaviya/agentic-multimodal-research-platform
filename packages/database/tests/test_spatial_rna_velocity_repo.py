"""Tests for SpatialRNAVelocityRepository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.spatial_rna_velocity_repo import SpatialRNAVelocityRepository


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
async def test_spatial_rna_velocity_repo_lifecycle(async_db: AsyncSession):
    repo = SpatialRNAVelocityRepository(async_db)

    study = await repo.create_study(
        tissue_sample_name="Developing Mouse Cortex",
        developmental_stage="E14.5",
        spot_count=3500,
        mean_velocity_magnitude=1.42,
        coherence_score=0.88,
    )
    assert study.id is not None

    await repo.add_vector_spot(
        study_id=study.id,
        spot_index=0,
        x_coord_um=120.5,
        y_coord_um=340.2,
        vx_vector=0.65,
        vy_vector=1.12,
        cell_type_annotation="Radial Glia",
    )

    await repo.add_streamline(
        study_id=study.id,
        streamline_id="Streamline-Cortex-01",
        origin_cell_state="Ventricular Progenitor",
        terminal_cell_state="Cortical Layer V/VI Pyramidal Neuron",
        pseudotime_length=3.4,
    )

    loaded = await repo.get_study_with_details(study.id)
    assert loaded is not None
    assert len(loaded.vector_spots) == 1
    assert len(loaded.streamlines) == 1
    assert loaded.streamlines[0].origin_cell_state == "Ventricular Progenitor"
