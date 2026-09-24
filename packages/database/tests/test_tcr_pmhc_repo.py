"""Tests for TCRpMHCRepository."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.repositories.tcr_pmhc_repo import TCRpMHCRepository


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
async def test_tcr_pmhc_repo_lifecycle(async_db: AsyncSession):
    repo = TCRpMHCRepository(async_db)

    study = await repo.create_study(
        tcr_name="NY-ESO-1_1G4",
        cdr3_alpha_seq="CAVRPTSGGSYIPTF",
        cdr3_beta_seq="CASSYVGNTGELFF",
        target_peptide="SLLMWITQC",
        hla_allele="HLA-A*02:01",
        binding_affinity_kd_um=4.8,
        immunogenicity_score=0.92,
    )
    assert study.id is not None

    await repo.add_cross_reactivity_record(
        study_id=study.id,
        self_peptide_seq="SLLMWITQV",
        tissue_expression="Testis / Placenta",
        predicted_cross_kd_um=120.0,
        off_target_risk_level="Low",
    )

    loaded = await repo.get_study_with_details(study.id)
    assert loaded is not None
    assert len(loaded.cross_reactivity_records) == 1
    assert loaded.cross_reactivity_records[0].off_target_risk_level == "Low"
