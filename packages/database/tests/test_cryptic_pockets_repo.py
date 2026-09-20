"""
Unit tests for Phase 107: Cryptic Pockets Database Repository.
"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.repositories.cryptic_pockets_repo import CrypticPocketRepository

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
async def test_cryptic_pockets_repo_crud(async_db: AsyncSession):
    repo = CrypticPocketRepository(async_db)

    # 1. Create analysis
    analysis = await repo.create_analysis(
        target_protein="KRAS-G12D",
        pdb_id="7T47",
        trajectory_frames_sampled=200,
        max_druggability_score=0.85,
        allosteric_coupling_score=0.74
    )
    assert analysis.id is not None
    assert analysis.target_protein == "KRAS-G12D"

    # 2. Add pockets
    pockets = await repo.add_pockets(
        analysis_id=analysis.id,
        pockets_data=[
            {
                "pocket_name": "Switch-II-Pocket",
                "center_x": 10.0,
                "center_y": 20.0,
                "center_z": 30.0,
                "apo_volume_a3": 100.0,
                "holo_volume_a3": 550.0,
                "volume_expansion_ratio": 5.5,
                "druggability_index": 0.85,
                "hydrophobicity_score": 0.80,
                "enclosing_residues": "GLY12, MET72"
            }
        ]
    )
    assert len(pockets) == 1

    # 3. Add coupled network
    networks = await repo.add_coupled_networks(
        analysis_id=analysis.id,
        networks_data=[
            {
                "source_residue": "MET72",
                "target_residue": "ASP210",
                "allosteric_correlation": 0.74,
                "pathway_shortest_distance_a": 15.2
            }
        ]
    )
    assert len(networks) == 1

    # 4. Fetch hydrated
    fetched = await repo.get_analysis(analysis.id)
    assert fetched is not None
    assert len(fetched.pockets) == 1
    assert len(fetched.coupled_networks) == 1
    assert fetched.detected_cryptic_pockets == 1
