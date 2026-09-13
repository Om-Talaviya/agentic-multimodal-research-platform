"""Tests for Knowledge Graph API routes (Phase 17)."""

from uuid import UUID
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from main import app
from database.connection import Base, get_db_session
from database.models.user import User as DBUser
from database.repositories.user_repo import UserRepository
from api.dependencies import get_current_user, get_optional_current_user
from shared.auth import User, UserRole, hash_password


@pytest.fixture
async def test_db():
    from database import connection as db_conn

    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    test_session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    orig_engine = db_conn.engine
    orig_maker = db_conn.async_session_maker

    db_conn.engine = test_engine
    db_conn.async_session_maker = test_session_maker

    # Create test user in DB
    async with test_session_maker() as session:
        user_repo = UserRepository(session)
        db_user = DBUser(
            id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
            username="graph_researcher",
            email="graph@platform.ai",
            password_hash=hash_password("GraphPass123!"),
            role=UserRole.RESEARCHER.value,
            is_active=True,
        )
        await user_repo.create(db_user)
        await session.commit()

    yield test_session_maker

    db_conn.engine = orig_engine
    db_conn.async_session_maker = orig_maker
    await test_engine.dispose()


@pytest.fixture
def sample_user():
    return User(
        id="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        username="graph_researcher",
        email="graph@platform.ai",
        role=UserRole.RESEARCHER,
        is_active=True,
    )


@pytest.mark.asyncio
async def test_graph_api_lifecycle(test_db, sample_user):
    async def override_get_session():
        async with test_db() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = override_get_session
    app.dependency_overrides[get_current_user] = lambda: sample_user
    app.dependency_overrides[get_optional_current_user] = lambda: sample_user

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Create Node A
            resp_a = await client.post(
                "/api/v1/graph/nodes",
                json={
                    "name": "Transformer Architecture",
                    "canonical_name": "Transformer",
                    "entity_type": "TECHNOLOGY",
                    "description": "Neural network architecture based on self-attention mechanisms.",
                    "aliases": ["Self-Attention Network"],
                },
            )
            assert resp_a.status_code == 201
            node_a = resp_a.json()
            assert node_a["name"] == "Transformer Architecture"
            node_a_id = node_a["id"]

            # 2. Create Node B
            resp_b = await client.post(
                "/api/v1/graph/nodes",
                json={
                    "name": "Attention Mechanism",
                    "entity_type": "CONCEPT",
                    "description": "Mechanism that dynamically weighs the relevance of input tokens.",
                },
            )
            assert resp_b.status_code == 201
            node_b = resp_b.json()
            node_b_id = node_b["id"]

            # 3. Create Edge between Node A and Node B
            resp_edge = await client.post(
                "/api/v1/graph/edges",
                json={
                    "source_id": node_a_id,
                    "target_id": node_b_id,
                    "relation_type": "DERIVED_FROM",
                    "description": "Transformers rely intrinsically on attention mechanisms.",
                    "weight": 1.0,
                    "confidence": 0.98,
                },
            )
            assert resp_edge.status_code == 201
            edge = resp_edge.json()
            edge_id = edge["id"]
            assert edge["relation_type"] == "DERIVED_FROM"

            # 4. List Nodes
            list_nodes = await client.get("/api/v1/graph/nodes")
            assert list_nodes.status_code == 200
            nodes_data = list_nodes.json()
            assert len(nodes_data) >= 2

            # 5. List Edges
            list_edges = await client.get("/api/v1/graph/edges")
            assert list_edges.status_code == 200
            edges_data = list_edges.json()
            assert len(edges_data) >= 1

            # 6. Get Subgraph
            subgraph_resp = await client.get(f"/api/v1/graph/subgraph?center_entity_id={node_a_id}&k_hops=1")
            assert subgraph_resp.status_code == 200
            subgraph_data = subgraph_resp.json()
            assert len(subgraph_data["nodes"]) >= 2
            assert len(subgraph_data["edges"]) >= 1

            # 7. Multi-hop Path Search
            path_resp = await client.get(
                "/api/v1/graph/paths",
                params={"source": "Transformer", "target": "Attention Mechanism"},
            )
            assert path_resp.status_code == 200
            path_data = path_resp.json()
            assert path_data["path_found"] is True
            assert path_data["hop_count"] == 1

            # 8. Stats
            stats_resp = await client.get("/api/v1/graph/stats")
            assert stats_resp.status_code == 200
            stats_data = stats_resp.json()
            assert stats_data["total_entities"] >= 2
            assert stats_data["total_relations"] >= 1

            # 9. Extract triplets endpoint
            extract_resp = await client.post(
                "/api/v1/graph/extract",
                json={
                    "text": "Quantum computers utilize Qubits to achieve superposition and quantum entanglement.",
                },
            )
            assert extract_resp.status_code == 200
            extract_data = extract_resp.json()
            assert "entities_count" in extract_data
            assert "relations_count" in extract_data

            # 10. Delete Edge & Node
            del_edge_resp = await client.delete(f"/api/v1/graph/edges/{edge_id}")
            assert del_edge_resp.status_code == 204

            del_node_resp = await client.delete(f"/api/v1/graph/nodes/{node_b_id}")
            assert del_node_resp.status_code == 204

            get_deleted = await client.get(f"/api/v1/graph/nodes/{node_b_id}")
            assert get_deleted.status_code == 404
    finally:
        app.dependency_overrides.clear()
