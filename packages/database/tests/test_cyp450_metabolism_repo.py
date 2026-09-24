"""Tests for CYP450MetabolismRepository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.cyp450_metabolism_repo import CYP450MetabolismRepository


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
async def test_cyp450_metabolism_repo_lifecycle(async_db: AsyncSession):
    repo = CYP450MetabolismRepository(async_db)

    screen = await repo.create_screen(
        compound_name="Ketoconazole",
        smiles="CC(=O)N1CCN(CC1)C2=CC=C(C=C2)OCC3COC(O3)(CN4C=CN=C4)C5=C(C=C(C=C5)Cl)Cl",
        intrinsic_clearance_ml_min_kg=12.4,
        hepatic_extraction_ratio=0.35,
        primary_metabolic_site="N-Dealkylation",
    )
    assert screen.id is not None

    await repo.add_isoform_profile(
        screen_id=screen.id,
        isoform_name="CYP3A4",
        inhibition_ic50_um=0.015,
        is_inhibitor=True,
        is_substrate=True,
    )

    await repo.add_clearance_record(
        screen_id=screen.id,
        incubation_time_min=30,
        parent_remaining_percent=68.5,
        metabolite_formation_area=14500.0,
    )

    loaded = await repo.get_screen_with_details(screen.id)
    assert loaded is not None
    assert len(loaded.isoform_profiles) == 1
    assert len(loaded.clearance_records) == 1
    assert loaded.isoform_profiles[0].is_inhibitor is True
