"""Tests for MultispecificTCellEngagerRepository (Phase 158)."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.multispecific_tcell_engager_repo import MultispecificTCellEngagerRepository


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
async def test_multispecific_tcell_engager_repo_lifecycle(async_db: AsyncSession):
    repo = MultispecificTCellEngagerRepository(async_db)

    study = await repo.create_study(
        construct_name="Test TriTE Construct",
        modality_format="TriTE",
        primary_tumor_antigen="HER2/EGFR",
        tcell_activation_arm="Anti-CD3e",
        synaptic_cleft_distance_a=115.0,
        cytolytic_potency_ec50_pm=15.0,
        perforin_granzyme_flux=40.0,
        crs_cytokine_risk_score=0.2,
    )
    assert study.id is not None

    await repo.add_binding_domain(
        study_id=study.id,
        arm_designation="Arm A",
        target_epitope="HER2",
        kd_affinity_nM=5.0,
        arm_length_angstrom=40.0,
        rotational_flexibility_deg=45.0,
    )

    await repo.add_synapse_profile(
        study_id=study.id,
        intermembrane_distance_nm=11.5,
        synapse_maturation_time_min=18.0,
        lytic_granule_polarization_pct=92.0,
        tumor_lysis_percentage=95.0,
    )

    loaded = await repo.get_study_with_details(study.id)
    assert loaded is not None
    assert len(loaded.binding_domains) == 1
    assert len(loaded.synapse_profiles) == 1
