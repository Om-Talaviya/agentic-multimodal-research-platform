"""Integration tests for Super-Graph REST API (Phase 44)."""
import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.connection import Base
from database.models.user import User as DBUser
from api.dependencies import get_current_user, get_db_session
from main import app

@pytest.fixture
async def async_test_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session
    
    await engine.dispose()

@pytest.fixture
def mock_user():
    return DBUser(
        id=uuid.uuid4(),
        username="systems_biology_lead",
        email="sysbio_lead@stanford.edu",
        password_hash="mocked",
        role="Researcher",
    )

@pytest.mark.asyncio
async def test_super_graph_api_lifecycle(async_test_session: AsyncSession, mock_user: DBUser):
    async def override_get_db():
        yield async_test_session

    async def override_get_user():
        return mock_user

    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_user

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. POST /api/v1/supergraph/init-seed
        res_seed = await client.post("/api/v1/supergraph/init-seed")
        assert res_seed.status_code == 201
        assert res_seed.json()["status"] == "SUCCESS"

        # 2. GET /api/v1/supergraph/nodes
        res_nodes = await client.get("/api/v1/supergraph/nodes")
        assert res_nodes.status_code == 200
        assert len(res_nodes.json()) >= 6

        # 3. GET /api/v1/supergraph/edges
        res_edges = await client.get("/api/v1/supergraph/edges")
        assert res_edges.status_code == 200
        assert len(res_edges.json()) >= 5

        # 4. POST /api/v1/supergraph/hypotheses/formulate
        req_hypo = {"focus_entity": "PCSK9"}
        res_hypo = await client.post("/api/v1/supergraph/hypotheses/formulate", json=req_hypo)
        assert res_hypo.status_code == 201
        hypos = res_hypo.json()
        assert len(hypos) >= 2
        assert "PCSK9" in hypos[0]["title"]

        # 5. GET /api/v1/supergraph/hypotheses
        res_list = await client.get("/api/v1/supergraph/hypotheses")
        assert res_list.status_code == 200
        assert len(res_list.json()) >= 2

    app.dependency_overrides.clear()
