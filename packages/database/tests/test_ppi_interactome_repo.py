"""
Tests for Phase 58: PPI Interactome Database Repository.
"""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from database.connection import Base
from database.repositories.ppi_interactome_repo import PPIInteractomeRepository


@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_ppi_repo_crud(async_session: AsyncSession):
    repo = PPIInteractomeRepository(async_session)

    # 1. Create Network
    net = await repo.create_network(
        network_name="KRAS Network",
        disease_context="Oncology",
    )
    assert net.id is not None

    # 2. Add Nodes and Edges
    await repo.add_nodes_and_edges(
        network_id=net.id,
        nodes_data=[
            {"gene_symbol": "KRAS", "uniprot_id": "P01116", "is_hub_target": True},
            {"gene_symbol": "BRAF", "uniprot_id": "P15056", "is_hub_target": False},
        ],
        edges_data=[
            {
                "source_protein": "KRAS",
                "target_protein": "BRAF",
                "binding_affinity_kd_nm": 12.0,
                "confidence_score": 0.98,
                "druggability_index": 0.92,
            }
        ],
    )

    # 3. Get Network
    fetched = await repo.get_network(net.id)
    assert fetched is not None
    assert fetched.total_nodes == 2
    assert fetched.total_edges == 1
    assert len(fetched.nodes) == 2
    assert len(fetched.edges) == 1
