"""Tests for MitochondrialBioenergeticsRepository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.mitochondrial_bioenergetics_repo import MitochondrialBioenergeticsRepository


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
async def test_mitochondrial_bioenergetics_repo_lifecycle(async_db: AsyncSession):
    repo = MitochondrialBioenergeticsRepository(async_db)

    study = await repo.create_study(
        cell_line_or_tissue="Cardiomyocytes",
        oxygen_consumption_rate_pmol_min=240.5,
        extracellular_acidification_rate=32.0,
        respiratory_control_ratio=5.8,
        membrane_potential_delta_psi_mv=-165.0,
    )
    assert study.id is not None

    await repo.add_complex_record(
        study_id=study.id,
        complex_name="Complex I",
        relative_activity_pct=96.4,
        proton_pumping_stoichiometry=4.0,
        inhibitor_sensitivity="Rotenone",
    )

    await repo.add_ros_profile(
        study_id=study.id,
        superoxide_flux_uM_s=0.045,
        h2o2_emission_rate=0.018,
        mptp_opening_probability=0.03,
        glutathione_redox_ratio=65.0,
    )

    loaded = await repo.get_study_with_details(study.id)
    assert loaded is not None
    assert len(loaded.etc_complexes) == 1
    assert len(loaded.ros_profiles) == 1
    assert loaded.etc_complexes[0].complex_name == "Complex I"
