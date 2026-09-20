"""
Unit tests for Phase 109: CyTOF Repository.
"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.repositories.cytof_repo import CyTOFRepository

@pytest.fixture
async def db_session():
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
async def test_cytof_repo_crud(db_session):
    repo = CyTOFRepository(db_session)

    exp = await repo.create_experiment(
        experiment_name="PBMC-CyTOF-Test",
        tissue_type="PBMC",
        cell_count=5000,
        panel_size=35,
        cofactor=5.0
    )

    assert exp.id is not None
    assert exp.experiment_name == "PBMC-CyTOF-Test"
    assert exp.cell_count == 5000

    ch = await repo.add_metal_channel(
        experiment_id=exp.id,
        channel_name="141Pr_CD3",
        metal_isotope="141Pr",
        target_marker="CD3",
        mean_intensity=450.0,
        signal_to_noise=24.5
    )

    assert ch.id is not None
    assert ch.target_marker == "CD3"

    cl = await repo.add_cluster(
        experiment_id=exp.id,
        cluster_id=1,
        cluster_name="CD4+ Central Memory T Cells",
        cell_frequency=22.0,
        marker_enrichment_profile={"CD3": 2.8, "CD4": 3.1},
        phenograph_k=30
    )

    assert cl.id is not None
    assert cl.cluster_name == "CD4+ Central Memory T Cells"

    channels = await repo.list_channels(exp.id)
    clusters = await repo.list_clusters(exp.id)
    assert len(channels) == 1
    assert len(clusters) == 1
