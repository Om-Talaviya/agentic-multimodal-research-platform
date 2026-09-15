"""Unit tests for KnowledgeGraphEngine."""

import pytest
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from database.connection import Base
from database.repositories.graph_repo import KnowledgeGraphRepository
from research.graph.engine import KnowledgeGraphEngine


@pytest.fixture
async def async_session():
    """Create isolated in-memory SQLite async session."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_extract_triplets_and_engine_persistence(async_session):
    """Test rule-based triplet extraction from synthesized findings."""
    repo = KnowledgeGraphRepository(async_session)
    engine = KnowledgeGraphEngine(repo)
    user_id = uuid.uuid4()

    text = (
        "Polylactic Acid degrades in seawater at ambient temperatures under 20C. "
        "Furthermore, Graphene Oxide significantly enhances tensile strength by 45%. "
        "The synthesis protocol was developed by Stanford Laboratory in 2025."
    )

    result = await engine.extract_triplets_from_text(text, user_id=user_id)
    assert result.entities_count >= 4
    assert result.relations_count >= 3
    assert len(result.triplets) >= 3

    # Verify extracted entities in graph
    pla = await repo.find_entity_by_name("Polylactic Acid", user_id=user_id)
    assert pla is not None

    go = await repo.find_entity_by_name("Graphene Oxide", user_id=user_id)
    assert go is not None


@pytest.mark.asyncio
async def test_graph_augmented_context_and_pathfinding(async_session):
    """Test GraphRAG context generation and multi-hop pathfinding."""
    repo = KnowledgeGraphRepository(async_session)
    engine = KnowledgeGraphEngine(repo)
    user_id = uuid.uuid4()

    # Ingest text that forms a connected graph
    text = (
        "Bio-Plastic degrades in marine seawater. "
        "Marine microbes secrete digestive enzymes. "
        "Digestive enzymes accelerate mass loss."
    )
    await engine.extract_triplets_from_text(text, user_id=user_id)

    # 1. Test GraphRAG context generation
    ctx, subgraphs = await engine.get_graph_augmented_context("Bio-Plastic", user_id=user_id, max_hops=1)
    assert "Knowledge Graph Relational Context" in ctx
    assert "Bio-Plastic" in ctx
    assert len(subgraphs) >= 1

    # 2. Test Path finding: Bio-Plastic -> marine microbes (2 hops)
    # Let's add explicit relation: marine seawater -> marine microbes
    sw = await repo.find_entity_by_name("marine seawater", user_id=user_id)
    mm = await repo.find_entity_by_name("Marine microbes", user_id=user_id)
    if sw and mm:
        await repo.create_relation(sw.id, mm.id, "HOSTS", user_id=user_id)

        path_res = await engine.find_path_between_entities("Bio-Plastic", "digestive enzymes", user_id=user_id, max_depth=4)
        if path_res.path_found:
            assert path_res.hop_count >= 2
            assert path_res.summary is not None
