"""Integration tests for Model Evaluation and Leaderboard REST endpoints."""
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4
import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from main import app
from api.dependencies import get_current_user, get_db_session, get_model_gateway, get_optional_current_user
from database.connection import Base
from database.models.user import User as DBUser
from database.repositories.user_repo import UserRepository
from ai.gateway.model_gateway import ModelGateway
from ai.registry.model_registry import ModelDefinition
from ai.schemas import LLMResponse, ModelCapability
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

    async def override_get_db_session():
        async with test_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = override_get_db_session

    yield test_session_maker

    app.dependency_overrides.pop(get_db_session, None)
    db_conn.engine = orig_engine
    db_conn.async_session_maker = orig_maker
    await test_engine.dispose()


@pytest.mark.asyncio
async def test_evaluate_and_leaderboard_endpoints(test_db):
    # Mock ModelGateway for deterministic evaluation
    mock_gateway = MagicMock()
    mock_gateway.complete = AsyncMock(return_value=LLMResponse(
        content="Step 1: Entanglement is a quantum mechanical phenomenon where particles share quantum states.",
        model="gemini-2.0-flash",
        usage={"prompt_tokens": 30, "completion_tokens": 25, "total_tokens": 55},
        metadata={"cost_usd": 0.00002},
    ))
    
    # Mock model registry with valid ModelDefinition
    mock_model_def = ModelDefinition(
        model_id="gemini-2.0-flash",
        provider_name="gemini",
        tier="paid",
        is_local=False,
        input_cost=0.0001,
        output_cost=0.0002,
        priority=15,
        capabilities={ModelCapability.REASONING, ModelCapability.EXTRACTION},
        task_suitability=["general", "long_form_research"],
    )

    mock_gateway.model_registry.list_models.return_value = [mock_model_def]
    mock_gateway.model_registry.get.return_value = mock_model_def

    app.dependency_overrides[get_model_gateway] = lambda: mock_gateway

    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Trigger evaluation
            eval_payload = {
                "model_id": "gemini-2.0-flash",
                "benchmark_name": "research_core_eval_v1"
            }
            eval_resp = await client.post("/api/v1/models/evaluate", json=eval_payload)
            assert eval_resp.status_code == 201
            eval_data = eval_resp.json()
            assert eval_data["model_id"] == "gemini-2.0-flash"
            assert "overall_score" in eval_data
            eval_id = eval_data["id"]

            # 2. Fetch evaluation detail
            detail_resp = await client.get(f"/api/v1/models/evaluations/{eval_id}")
            assert detail_resp.status_code == 200
            detail_data = detail_resp.json()
            assert len(detail_data["sample_results"]) > 0

            # 3. List evaluations
            list_resp = await client.get("/api/v1/models/evaluations")
            assert list_resp.status_code == 200
            assert len(list_resp.json()) >= 1

            # 4. Fetch leaderboard
            board_resp = await client.get("/api/v1/models/leaderboard")
            assert board_resp.status_code == 200
            board_data = board_resp.json()
            assert len(board_data) >= 1
            assert board_data[0]["model_id"] == "gemini-2.0-flash"
            assert board_data[0]["overall_score"] > 0.0

            # 5. Delete evaluation
            del_resp = await client.delete(f"/api/v1/models/evaluations/{eval_id}")
            assert del_resp.status_code == 204
    finally:
        app.dependency_overrides.pop(get_model_gateway, None)
