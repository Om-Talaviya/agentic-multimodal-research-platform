"""Tests for Phase 578: Autonomous Xenobiotic Polyethylene Terephthalate (PET) Plastic Enzymatic Depolymerase Engineering & Micro-Solvation Energy Forecaster repository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.xenobiotic_pet_depolymerase_repo import XenobioticPetDepolymeraseRepository


@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_xenobiotic_pet_depolymerase_repository(async_session: AsyncSession):
    repo = XenobioticPetDepolymeraseRepository(async_session)

    study = await repo.create_study(
        name="Autonomous Xenobiotic PET Plastic Enzymatic Depolymerase Engineering Benchmark",
        target_enzyme="Ideonella sakaiensis PETase Engineered Variant (Fast-PETase/LCC-ICCG)",
        substrate_type="Post-Consumer Highly Crystalline Polyethylene Terephthalate (PET, 35% crystallinity)",
        catalytic_efficiency_kcat_km=142.5,
        melting_temperature_tm_celsius=78.2,
        solvation_free_energy_barrier_kcal=14.8,
        depolymerization_yield_percent=94.6,
        confidence_score=0.997,
        status="completed",
        summary_report="Automated validation benchmark passed successfully.",
    )
    assert study.id is not None
    assert study.name == "Autonomous Xenobiotic PET Plastic Enzymatic Depolymerase Engineering Benchmark"
    assert study.catalytic_efficiency_kcat_km == 142.5
    assert study.melting_temperature_tm_celsius == 78.2
    assert study.confidence_score == 0.997

    profile = await repo.add_item_profile(
        study_id=study.id,
        item_name="Active_Site_Cleft_Trp159_Phe238_Hydrophobic_Clamp",
        quantitative_value=168.4,
        profile_category="Catalytic Subsite",
        log2_fold_change=2.1,
        significance_score=0.98,
    )
    assert profile.id is not None
    assert profile.study_id == study.id
    assert profile.item_name == "Active_Site_Cleft_Trp159_Phe238_Hydrophobic_Clamp"

    trace = await repo.add_metric_trace(
        study_id=study.id,
        metric_dimension="solvation_free_energy_barrier_kcal",
        observed_value=14.8,
        z_score=2.85,
        p_value=0.001,
    )
    assert trace.id is not None
    assert trace.study_id == study.id

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.id == study.id

    studies = await repo.list_studies()
    assert len(studies) >= 1
