"""Integration tests for In-Silico Reproducibility REST API endpoints."""

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
        username="repro_api_user",
        email="repro@test.com",
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
async def test_reproducibility_api_lifecycle(api_client: AsyncClient):
    """Test protocol registration, in-silico execution, claim verification, and metrics via REST API."""
    # 1. Register Protocol
    create_resp = await api_client.post(
        "/api/v1/reproducibility/protocols",
        json={
            "name": "Transformer Self-Attention Matrix Complexity",
            "executable_code": """
import math
seq_len = 1024
d_model = 64
flops = 2 * (seq_len ** 2) * d_model
metrics = {"attention_flops": flops, "scale_factor": round(1.0 / math.sqrt(d_model), 4)}
""",
            "parameters": {"seq_len": 1024, "d_model": 64},
            "claimed_metrics": {"attention_flops": 134217728.0, "scale_factor": 0.1250},
        },
    )
    assert create_resp.status_code == 201
    proto_data = create_resp.json()
    protocol_id = proto_data["id"]
    assert proto_data["name"] == "Transformer Self-Attention Matrix Complexity"

    # 2. Execute In-Silico Simulation
    exec_resp = await api_client.post(
        f"/api/v1/reproducibility/protocols/{protocol_id}/execute",
        json={"tolerance_threshold": 0.05},
    )
    assert exec_resp.status_code == 201
    exec_data = exec_resp.json()
    assert exec_data["status"] == "succeeded"
    assert exec_data["overall_status"] == "fully_reproduced"
    assert exec_data["reproducibility_score"] >= 0.90
    assert len(exec_data["traces"]) == 2

    # 3. Fetch Protocol with verification traces
    detail_resp = await api_client.get(f"/api/v1/reproducibility/protocols/{protocol_id}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert len(detail_data["runs"]) == 1
    assert len(detail_data["verification_traces"]) == 2

    # 4. Check Platform Metrics
    metrics_resp = await api_client.get("/api/v1/reproducibility/metrics")
    assert metrics_resp.status_code == 200
    metrics_data = metrics_resp.json()
    assert metrics_data["total_protocols"] >= 1
    assert metrics_data["total_runs"] >= 1
    assert metrics_data["reproduced_claims"] >= 2
