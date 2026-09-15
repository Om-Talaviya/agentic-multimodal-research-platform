"""Unit tests for Drug Repurposing & Synergy Repository (Phase 45)."""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from database.connection import Base
from database.repositories.drug_synergy_repo import DrugSynergyRepository

@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_drug_synergy_repo_crud(async_session: AsyncSession):
    repo = DrugSynergyRepository(async_session)

    # 1. Create Screen
    screen = await repo.create_screen(
        title="Glioblastoma Approved Drug Repurposing Campaign",
        disease_indication="Glioblastoma",
        total_screened=2450,
    )
    assert screen.id is not None
    assert screen.disease_indication == "Glioblastoma"

    # 2. Add Candidates
    cands_data = [
        {
            "drug_name": "Niclosamide",
            "original_indication": "Anthelmintic",
            "proposed_mechanism": "Wnt/beta-catenin inhibition.",
            "connectivity_score": -0.925,
            "ic50_um": 0.85,
        }
    ]
    await repo.add_candidates(screen.id, cands_data)
    cands = await repo.get_candidates(screen.id)
    assert len(cands) == 1
    assert cands[0].drug_name == "Niclosamide"

    # 3. Add Synergies
    syn_data = [
        {
            "drug_a": "Niclosamide",
            "drug_b": "Temozolomide",
            "zip_synergy_score": 19.85,
            "loewe_combination_index": 0.58,
        }
    ]
    await repo.add_synergies(screen.id, syn_data)
    synergies = await repo.get_synergies(screen.id)
    assert len(synergies) == 1
    assert synergies[0].zip_synergy_score == 19.85

    # 4. List & Delete
    screens = await repo.list_screens()
    assert len(screens) == 1
    deleted = await repo.delete_screen(screen.id)
    assert deleted is True
