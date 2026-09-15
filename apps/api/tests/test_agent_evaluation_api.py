"""Integration tests for Autonomous Agent Evaluation REST endpoints."""
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4
import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from main import app
from api.dependencies import get_current_user, get_db_session, get_optional_current_user
from database.connection import Base
from database.models.user import User as DBUser
from database.repositories.user_repo import UserRepository
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
async def test_agent_evaluations_endpoints(test_db):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Trigger agent evaluation
        eval_payload = {
            "agent_name": "WebResearchAgent",
            "research_objective": "Transformer scaling laws exploration",
            "plan_tasks": [{"title": "Search transformer papers"}, {"title": "Synthesize scaling laws"}],
            "step_telemetry": [
                {
                    "step_index": 1,
                    "agent_type": "WebResearchAgent",
                    "action_type": "tool_execution",
                    "tool_name": "web_search",
                    "tool_args": {"query": "transformer scaling laws"},
                    "tool_output_length": 150,
                    "success": True,
                    "latency_ms": 110,
                    "tokens_consumed": 50,
                },
                {
                    "step_index": 2,
                    "agent_type": "WebResearchAgent",
                    "action_type": "synthesis",
                    "tool_name": "synthesize",
                    "tool_args": {},
                    "tool_output_length": 300,
                    "success": True,
                    "latency_ms": 250,
                    "tokens_consumed": 150,
                },
            ],
            "evidence_items": [{"content": "Transformer architectures exhibit power law scaling with compute."}],
            "report_text": "Transformer architectures exhibit power law scaling with compute resources.",
            "claims": ["Transformer architectures exhibit power law scaling with compute resources."],
            "execution_time_ms": 360,
            "total_tokens": 200,
            "cost_usd": 0.00004,
        }

        create_resp = await client.post("/api/v1/agents/evaluate", json=eval_payload)
        assert create_resp.status_code == 201
        data = create_resp.json()
        assert data["agent_name"] == "WebResearchAgent"
        assert data["plan_precision"] > 0.0
        assert data["tool_accuracy"] == 1.0
        assert data["hallucination_rate"] == 0.0
        eval_id = data["id"]

        # 2. Get evaluation by ID
        detail_resp = await client.get(f"/api/v1/agents/evaluations/{eval_id}")
        assert detail_resp.status_code == 200
        detail_data = detail_resp.json()
        assert detail_data["id"] == eval_id
        assert detail_data["agent_name"] == "WebResearchAgent"
        assert len(detail_data["steps"]) == 2

        # 3. List evaluations
        list_resp = await client.get("/api/v1/agents/evaluations?agent_name=WebResearchAgent")
        assert list_resp.status_code == 200
        evals_list = list_resp.json()
        assert len(evals_list) >= 1

        # 4. Get metrics summary
        summary_resp = await client.get("/api/v1/agents/metrics/summary")
        assert summary_resp.status_code == 200
        summary_data = summary_resp.json()
        assert summary_data["total_evaluations"] >= 1
        assert "avg_score" in summary_data

        # 5. Delete evaluation
        del_resp = await client.delete(f"/api/v1/agents/evaluations/{eval_id}")
        assert del_resp.status_code == 204

        # Verify deletion
        get_deleted = await client.get(f"/api/v1/agents/evaluations/{eval_id}")
        assert get_deleted.status_code == 404
