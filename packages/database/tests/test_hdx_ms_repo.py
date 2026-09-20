"""
Unit tests for Phase 105: HDX-MS Database Repository.
"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.repositories.hdx_ms_repo import HDXMassSpecRepository

@pytest.fixture
async def async_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.asyncio
async def test_hdx_ms_repo_crud(async_db: AsyncSession):
    repo = HDXMassSpecRepository(async_db)

    # 1. Create experiment
    exp = await repo.create_experiment(
        protein_name="PCSK9",
        uniprot_id="P07550",
        state_condition="LIGAND_BOUND",
        sequence_coverage_pct=92.5,
        redundancy_score=3.2
    )
    assert exp.id is not None
    assert exp.protein_name == "PCSK9"

    # 2. Add uptake curves
    curves = await repo.add_uptake_curves(
        experiment_id=exp.id,
        curves_data=[
            {
                "peptide_sequence": "MGTVSSRRA",
                "start_res": 1,
                "end_res": 9,
                "timepoint_seconds": 60.0,
                "deuterium_uptake_da": 3.5,
                "fractional_uptake_pct": 45.0,
                "protection_factor_ln_p": 2.1
            }
        ]
    )
    assert len(curves) == 1

    # 3. Add protection map
    maps = await repo.add_protection_maps(
        experiment_id=exp.id,
        maps_data=[
            {
                "residue_number": 1,
                "amino_acid": "M",
                "protection_factor": 2.5,
                "solvent_accessibility_level": "BURY_PROTECTED",
                "delta_uptake_apo_vs_bound": 22.4
            }
        ]
    )
    assert len(maps) == 1

    # 4. Fetch hydrated
    fetched = await repo.get_experiment(exp.id)
    assert fetched is not None
    assert len(fetched.uptake_curves) == 1
    assert len(fetched.protection_maps) == 1
    assert fetched.total_peptides == 1
