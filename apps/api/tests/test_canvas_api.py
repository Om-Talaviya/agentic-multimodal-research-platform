import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.dependencies import get_current_user, get_db_session
from database.connection import Base
from database.models.user import User
from main import app


@pytest.fixture
async def api_client():
    """Create test client with in-memory SQLite and auth override."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    test_user = User(
        id=uuid.uuid4(),
        username="canvas_researcher",
        email="canvas@test.com",
        password_hash="hash",
        role="researcher",
    )

    async def override_get_db_session():
        async with async_session_factory() as session:
            yield session

    async def override_get_current_user():
        return test_user

    async with async_session_factory() as session:
        session.add(test_user)
        await session.commit()

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_current_user] = override_get_current_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_canvas_api_full_workflow(api_client: AsyncClient):
    """Test canvas board creation, node/edge manipulation, auto-generation, metrics, and brainstorm."""
    # 1. Create Board
    create_resp = await api_client.post(
        "/api/v1/canvas/boards",
        json={
            "title": "Quantum Neural Circuit Synthesis",
            "description": "Visual DAG modeling variational quantum circuits.",
            "background_grid": "dots",
        },
    )
    assert create_resp.status_code == 201
    board_data = create_resp.json()
    board_id = board_data["id"]
    assert board_data["title"] == "Quantum Neural Circuit Synthesis"

    # 2. List Boards
    list_resp = await api_client.get("/api/v1/canvas/boards")
    assert list_resp.status_code == 200
    boards = list_resp.json()
    assert len(boards) >= 1

    # 3. Add Node
    node_resp = await api_client.post(
        f"/api/v1/canvas/boards/{board_id}/nodes",
        json={
            "node_type": "hypothesis",
            "title": "Ansatz Expressibility Bound",
            "content": "Depth-6 circuits avoid barren plateaus with local cost functions.",
            "confidence_score": 0.89,
            "status": "verified",
            "position_x": 150.0,
            "position_y": 200.0,
            "width": 280.0,
            "height": 160.0,
        },
    )
    assert node_resp.status_code == 201
    node1_id = node_resp.json()["id"]

    # 4. Add Second Node
    node2_resp = await api_client.post(
        f"/api/v1/canvas/boards/{board_id}/nodes",
        json={
            "node_type": "evidence",
            "title": "Pennylane Gradient Benchmarks",
            "content": "Gradients non-vanishing across 24 qubits.",
            "confidence_score": 0.94,
            "status": "verified",
            "position_x": 500.0,
            "position_y": 200.0,
        },
    )
    assert node2_resp.status_code == 201
    node2_id = node2_resp.json()["id"]

    # 5. Add Edge
    edge_resp = await api_client.post(
        f"/api/v1/canvas/boards/{board_id}/edges",
        json={
            "source_node_id": node1_id,
            "target_node_id": node2_id,
            "relation_type": "supports",
            "label": "grounded_by",
            "weight": 0.95,
        },
    )
    assert edge_resp.status_code == 201

    # 6. Auto-Generate from Research
    gen_resp = await api_client.post(
        f"/api/v1/canvas/boards/{board_id}/generate",
        json={
            "title": "Quantum Error Mitigation",
            "objective": "Zero noise extrapolation benchmarks",
            "findings": [{"topic": "Richardson Extrapolation", "summary": "3.8x SNR boost"}],
            "evidence": [{"claim": "Qiskit Aer noisy simulation", "source": "IBM Q 2026"}],
            "conclusions": ["Sufficient for near-term quantum advantage."],
        },
    )
    assert gen_resp.status_code == 201
    assert gen_resp.json()["total_nodes_generated"] >= 4

    # 7. Multi-Agent Brainstorm
    brainstorm_resp = await api_client.post(
        f"/api/v1/canvas/boards/{board_id}/brainstorm",
        json={"topic": "Quantum Circuit Depth"},
    )
    assert brainstorm_resp.status_code == 201
    assert brainstorm_resp.json()["brainstormed_nodes_count"] >= 2

    # 8. Get Board detail
    detail_resp = await api_client.get(f"/api/v1/canvas/boards/{board_id}")
    assert detail_resp.status_code == 200
    detail = detail_resp.json()
    assert len(detail["nodes"]) >= 6

    # 9. Get Platform Metrics
    metrics_resp = await api_client.get("/api/v1/canvas/metrics")
    assert metrics_resp.status_code == 200
    metrics = metrics_resp.json()
    assert metrics["total_canvas_boards"] >= 1
    assert metrics["total_canvas_nodes"] >= 6
