"""Unit tests for VirtualHTSRepository (Phase 54)."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.models.vhts import (
    DBVirtualHTSScreen,
    DBVirtualHTSHit,
    DBHTSClusterGroup,
)
from database.repositories.vhts_repo import VirtualHTSRepository


@pytest.fixture
async def db_session():
    """Create in-memory SQLite database session for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_vhts_repo_lifecycle(db_session: AsyncSession):
    repo = VirtualHTSRepository(db_session)

    # 1. Create Screen
    screen = await repo.create_screen(
        target_protein_name="EGFR Kinase Domain",
        pdb_id="7L11",
        total_screened=100000,
    )
    assert screen.id is not None
    assert screen.pdb_id == "7L11"

    # 2. Add Hits
    hit1 = await repo.add_hit(
        screen_id=screen.id,
        compound_id="CMP-001",
        smiles="CC(C)Nc1ncccc1",
        docking_score_kcal_mol=-10.5,
        pains_filter_passed=True,
    )
    assert hit1.id is not None
    assert hit1.docking_score_kcal_mol == -10.5

    hit2 = await repo.add_hit(
        screen_id=screen.id,
        compound_id="CMP-002",
        smiles="O=C(Nc1ccccc1)c2ccccc2",
        docking_score_kcal_mol=-11.8,
        pains_filter_passed=True,
    )
    assert hit2.docking_score_kcal_mol == -11.8

    # 3. Add Cluster
    cluster = await repo.add_cluster(
        screen_id=screen.id,
        cluster_label="Quinazoline Scaffold",
        scaffold_smiles="c1cnc2ccccc2n1",
        member_hits_count=2,
        mean_affinity_kcal_mol=-11.15,
    )
    assert cluster.id is not None

    # 4. List Hits & Clusters
    hits = await repo.list_hits(screen.id)
    clusters = await repo.list_clusters(screen.id)
    assert len(hits) == 2
    assert len(clusters) == 1

    # 5. Verify Metrics
    metrics = await repo.get_metrics()
    assert metrics["total_screens"] == 1
    assert metrics["total_hits_discovered"] == 2
    assert metrics["best_affinity_kcal_mol"] == -11.8
