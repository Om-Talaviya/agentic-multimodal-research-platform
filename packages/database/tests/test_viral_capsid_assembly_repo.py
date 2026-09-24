"""Tests for CapsidAssemblyRepository (Phase 151)."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.viral_capsid_assembly_repo import CapsidAssemblyRepository


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
async def test_viral_capsid_assembly_repo_lifecycle(async_db: AsyncSession):
    repo = CapsidAssemblyRepository(async_db)

    study = await repo.create_study(
        serotype_name="AAV2-Wildtype",
        triangulation_number="T=1",
        vp_stoichiometry_ratio="1:1:10",
        assembly_yield_percent=91.0,
        gibbs_free_energy_kcal_mol=-1100.0,
        critical_nucleus_size=5,
        full_empty_capsid_ratio=4.5,
    )
    assert study.id is not None

    await repo.add_interface(
        study_id=study.id,
        symmetry_axis="5-fold",
        delta_g_binding_kcal_mol=-25.0,
        buried_surface_area_a2=4500.0,
        hydrogen_bonds_count=30,
        salt_bridges_count=10,
    )

    await repo.add_trajectory(
        study_id=study.id,
        oligomer_size=60,
        forward_rate_k_on=1.0e6,
        reverse_rate_k_off=0.05,
        fraction_assembled=0.95,
    )

    loaded = await repo.get_study_with_details(study.id)
    assert loaded is not None
    assert len(loaded.interfaces) == 1
    assert len(loaded.trajectories) == 1
