"""Tests for quota-aware routing and fallback in ModelGateway."""

import pytest
import pytest_asyncio
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from ai.gateway.model_gateway import ModelGateway
from ai.providers.base import LLMProvider
from ai.providers.router import ModelRouter
from ai.registry.model_registry import ModelDefinition, ModelRegistry
from ai.registry.provider_registry import ProviderRegistry
from ai.schemas import LLMRequest, LLMResponse, ModelCapability
from database.connection import Base
from database.models.user import User as DBUser
from database.repositories.user_repo import UserRepository
from database.repositories.quota_repo import UserQuotaRepository
from database.repositories.usage_repo import UsageRepository
from shared.exceptions import QuotaExceededError


class MockLLM(LLMProvider):
    def __init__(self, name: str, models: list[str], is_local: bool = True):
        self._name = name
        self._models = models
        self._is_local = is_local
        self._capabilities = [ModelCapability.REASONING]

    @property
    def name(self) -> str:
        return self._name

    @property
    def models(self) -> list[str]:
        return self._models

    @property
    def is_local(self) -> bool:
        return self._is_local

    @property
    def capabilities(self) -> list[ModelCapability]:
        return self._capabilities

    async def complete(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            content=f"Response from {self.name}:{request.model}",
            model=request.model or self._models[0],
            usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
        )

    async def stream_complete(self, request: LLMRequest):
        yield f"token from {self.name}"

    async def health_check(self):
        from ai.schemas import ProviderHealth
        return ProviderHealth(provider=self.name, healthy=True)


@pytest_asyncio.fixture
async def db_context():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    @asynccontextmanager
    async def session_factory():
        async with session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    yield session_factory, session_maker
    await engine.dispose()


@pytest.mark.asyncio
async def test_quota_aware_fallback_skips_exhausted_model_and_records_on_fallback(db_context):
    session_factory, session_maker = db_context

    # 1. Create user with finite cost limit ($0.001)
    async with session_maker() as session:
        user_repo = UserRepository(session)
        quota_repo = UserQuotaRepository(session)

        user = DBUser(username="quota_user", email="quota_user@example.com", password_hash="hash")
        await user_repo.create(user)
        await session.commit()

        # Set finite cost limit of $0.0005 (Model A estimated cost will exceed this, Model B is free)
        await quota_repo.set_quota_limits(user_id=user.id, daily_cost_limit=0.0005)
        await session.commit()
        user_id = user.id

    # 2. Setup Registries
    # Model A: Expensive Paid model ($0.01 per 1K tokens)
    # Model B: Free Local model ($0.0 per 1K tokens)
    model_reg = ModelRegistry()
    model_reg.register(
        ModelDefinition(
            model_id="expensive-cloud-model",
            provider_name="cloud-provider",
            capabilities={ModelCapability.REASONING},
            tier="paid",
            input_cost=0.01,
            output_cost=0.02,
            priority=20,  # higher priority normally
            is_local=False,
        )
    )
    model_reg.register(
        ModelDefinition(
            model_id="free-local-model",
            provider_name="local-provider",
            capabilities={ModelCapability.REASONING},
            tier="free",
            input_cost=0.0,
            output_cost=0.0,
            priority=10,
            is_local=True,
        )
    )

    prov_reg = ProviderRegistry()
    prov_reg.register_llm(MockLLM("cloud-provider", ["expensive-cloud-model"], is_local=False))
    prov_reg.register_llm(MockLLM("local-provider", ["free-local-model"], is_local=True))

    router = ModelRouter(model_registry=model_reg, provider_registry=prov_reg)
    gateway = ModelGateway(
        router=router,
        model_registry=model_reg,
        provider_registry=prov_reg,
        session_factory=session_factory,
    )

    # 3. Complete request with user_id attached
    req = LLMRequest(
        model="expensive-cloud-model",
        messages=[{"role": "user", "content": "Hello"}],
        metadata={"user_id": str(user_id)},
    )
    response = await gateway.complete(req)

    # Verify that Model A was skipped due to quota and Model B was invoked
    assert response.model == "free-local-model"
    assert response.metadata["fallback_occurred"] is True

    # Verify usage was recorded against Model B (not Model A)
    async with session_maker() as session:
        usage_repo = UsageRepository(session)
        records = await usage_repo.get_user_usage(user_id)
        assert len(records) == 1
        assert records[0].model == "free-local-model"
        assert records[0].provider == "local-provider"
        assert records[0].cost_usd == 0.0


@pytest.mark.asyncio
async def test_all_models_quota_exhausted_raises_quota_exceeded_error(db_context):
    session_factory, session_maker = db_context

    # 1. Create user with 0 token limit
    async with session_maker() as session:
        user_repo = UserRepository(session)
        quota_repo = UserQuotaRepository(session)

        user = DBUser(username="exhausted_user", email="exhausted@example.com", password_hash="hash")
        await user_repo.create(user)
        await session.commit()

        # Set finite limit of 50 tokens (our request needs ~1000 tokens)
        await quota_repo.set_quota_limits(user_id=user.id, daily_token_limit=50)
        await session.commit()
        user_id = user.id

    model_reg = ModelRegistry()
    model_reg.register(
        ModelDefinition(
            model_id="model-1",
            provider_name="prov-1",
            capabilities={ModelCapability.REASONING},
            priority=10,
        )
    )

    prov_reg = ProviderRegistry()
    prov_reg.register_llm(MockLLM("prov-1", ["model-1"]))

    router = ModelRouter(model_registry=model_reg, provider_registry=prov_reg)
    gateway = ModelGateway(
        router=router,
        model_registry=model_reg,
        provider_registry=prov_reg,
        session_factory=session_factory,
    )

    req = LLMRequest(
        messages=[{"role": "user", "content": "Test"}],
        metadata={"user_id": str(user_id)},
    )

    with pytest.raises(QuotaExceededError):
        await gateway.complete(req)
