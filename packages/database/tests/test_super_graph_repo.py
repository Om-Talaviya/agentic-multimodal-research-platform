"""Unit tests for Super-Graph Repository (Phase 44)."""
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from database.connection import Base
from database.repositories.super_graph_repo import SuperGraphRepository

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
async def test_super_graph_repo_crud(async_session: AsyncSession):
    repo = SuperGraphRepository(async_session)

    # 1. Create Nodes
    n1 = await repo.create_node(
        canonical_id="HGNC:PCSK9",
        label="PCSK9",
        entity_type="Gene",
        degree_centrality=0.38,
    )
    n2 = await repo.create_node(
        canonical_id="MESH:D006528",
        label="Hepatocellular Carcinoma",
        entity_type="Disease",
        degree_centrality=0.65,
    )
    assert n1.id is not None
    assert n2.id is not None

    # 2. Create Edge
    edge = await repo.create_edge(
        source_node_id=n1.id,
        target_node_id=n2.id,
        relation_type="ASSOCIATED_WITH",
        confidence_score=0.95,
        is_predicted=False,
    )
    assert edge.id is not None
    assert edge.relation_type == "ASSOCIATED_WITH"

    # 3. Create Hypothesis
    hypo = await repo.create_hypothesis(
        title="PCSK9 and PI3K-Akt Synergistic Axis in HCC",
        premise_statement="Inhibiting PCSK9 blocks lipid raft-mediated Akt activation.",
        mechanistic_chain=["PCSK9 Inhibition", "LDLR Surface Retention", "Akt Downregulation"],
        novelty_score=0.92,
        biological_plausibility=0.94,
    )
    assert hypo.id is not None
    assert hypo.novelty_score == 0.92

    # 4. List
    nodes = await repo.list_nodes()
    assert len(nodes) == 2
    edges = await repo.list_edges()
    assert len(edges) == 1
    hypotheses = await repo.list_hypotheses()
    assert len(hypotheses) == 1
