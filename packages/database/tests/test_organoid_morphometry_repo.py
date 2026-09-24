"""Tests for OrganoidMorphometryRepository (Phase 147)."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.organoid_morphometry_repo import OrganoidMorphometryRepository


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
async def test_organoid_morphometry_repo_lifecycle(async_db: AsyncSession):
    repo = OrganoidMorphometryRepository(async_db)

    study = await repo.create_study(
        study_name="Patient Spheroid Test",
        tumor_type="Glioblastoma",
        organoid_count=1,
        mean_diameter_um=450.0,
        mean_volume_um3=38000000.0,
        sphericity_index=0.91,
        necrotic_core_ratio=0.12,
        hypoxia_gradient_slope=-0.001,
    )
    assert study.id is not None

    await repo.add_z_stack(
        study_id=study.id,
        slice_depth_um=50.0,
        cross_sectional_area_um2=120000.0,
        circularity=0.92,
        fluorescence_intensity=750.0,
        live_dead_ratio=4.5,
    )

    await repo.add_dose_response(
        study_id=study.id,
        compound_name="Temozolomide",
        dose_uM=10.0,
        viability_pct=65.0,
        invasion_inhibition_pct=40.0,
        computed_ic50_uM=12.5,
    )

    loaded = await repo.get_study_with_details(study.id)
    assert loaded is not None
    assert len(loaded.z_stacks) == 1
    assert len(loaded.dose_responses) == 1
