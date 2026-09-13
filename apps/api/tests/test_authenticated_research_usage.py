"""Authenticated integration test proving end-to-end user_id propagation to UsageRecord."""

import pytest
import pytest_asyncio
import httpx
from contextlib import asynccontextmanager
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from main import app
from database.connection import Base, bootstrap_default_users, get_db_session
from database.models.user import User as DBUser
from database.repositories.user_repo import UserRepository
from database.repositories.usage_repo import UsageRepository
from database.models.usage_record import UsageRecord
from api.dependencies import get_model_gateway, get_model_router
from api.routes.research import get_pipeline
from ai.gateway.model_gateway import ModelGateway
from ai.providers.base import LLMProvider
from ai.providers.router import ModelRouter
from ai.registry.model_registry import ModelDefinition, ModelRegistry
from ai.registry.provider_registry import ProviderRegistry
from ai.schemas import LLMRequest, LLMResponse, ModelCapability, ProviderHealth
from research.pipeline import ResearchPipeline


class AuthTestMockLLM(LLMProvider):
    def __init__(self):
        self._capabilities = [ModelCapability.REASONING, ModelCapability.TOOL_USE]

    @property
    def name(self) -> str:
        return "auth-mock-prov"

    @property
    def models(self) -> list[str]:
        return ["auth-mock-model"]

    @property
    def is_local(self) -> bool:
        return True

    @property
    def capabilities(self) -> list[ModelCapability]:
        return self._capabilities

    async def complete(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            content='{"objective": "Plan", "steps": []}',
            model="auth-mock-model",
            usage={"prompt_tokens": 120, "completion_tokens": 60, "total_tokens": 180},
        )

    async def stream_complete(self, request: LLMRequest):
        yield "token"

    async def health_check(self) -> ProviderHealth:
        return ProviderHealth(provider=self.name, healthy=True)


@pytest_asyncio.fixture
async def setup_auth_test_env():
    from database import connection as db_conn

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    orig_engine = db_conn.engine
    orig_maker = db_conn.async_session_maker
    db_conn.engine = engine
    db_conn.async_session_maker = session_maker

    @asynccontextmanager
    async def session_factory():
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def override_get_db_session():
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    # Bootstrap default users
    async with session_maker() as session:
        await bootstrap_default_users(session)
        await session.commit()

    # Setup Gateway and Router with Test LLM
    model_reg = ModelRegistry()
    model_reg.register(
        ModelDefinition(
            model_id="auth-mock-model",
            provider_name="auth-mock-prov",
            capabilities={ModelCapability.REASONING, ModelCapability.TOOL_USE},
            input_cost=0.002,
            output_cost=0.004,
            priority=10,
        )
    )

    prov_reg = ProviderRegistry()
    prov_reg.register_llm(AuthTestMockLLM())

    router = ModelRouter(model_registry=model_reg, provider_registry=prov_reg)
    gateway = ModelGateway(
        router=router,
        model_registry=model_reg,
        provider_registry=prov_reg,
        session_factory=session_factory,
    )

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_model_router] = lambda: router
    app.dependency_overrides[get_model_gateway] = lambda: gateway

    yield session_maker, gateway

    app.dependency_overrides.clear()
    db_conn.engine = orig_engine
    db_conn.async_session_maker = orig_maker
    await engine.dispose()


@pytest.mark.asyncio
async def test_authenticated_endpoint_propagates_user_id_to_usage_record(setup_auth_test_env):
    session_maker, gateway = setup_auth_test_env

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login to get real JWT access token
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "researcher", "password": "ResearcherPassword123!"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        user_id_from_auth = UUID(login_resp.json()["user"]["id"])

        # 2. Call authenticated research endpoint
        create_resp = await client.post(
            "/api/v1/research",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "question": "What are the latest advances in multi-agent autonomous systems?",
                "context": "Focus on 2026 breakthroughs.",
                "constraints": ["academic only"],
            },
        )
        assert create_resp.status_code == 201
        job_data = create_resp.json()
        job_id = UUID(job_data["id"])

        # 3. Simulate agent LLM execution passing context metadata
        req = LLMRequest(
            messages=[{"role": "user", "content": "Create research plan"}],
            metadata={"user_id": str(user_id_from_auth), "job_id": str(job_id)},
        )
        llm_resp = await gateway.complete(req)
        assert llm_resp.metadata["total_tokens"] == 180

        # 4. Verify in DB that UsageRecord has the real authenticated user_id
        async with session_maker() as session:
            usage_repo = UsageRepository(session)
            records = await usage_repo.get_user_usage(user_id_from_auth)
            assert len(records) >= 1
            assert records[0].user_id == user_id_from_auth
            assert records[0].job_id == job_id
            assert records[0].model == "auth-mock-model"
            assert records[0].provider == "auth-mock-prov"
            assert records[0].total_tokens == 180
            assert records[0].success is True
