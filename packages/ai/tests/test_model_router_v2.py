"""Unit tests for ModelRouter v2 (capability, task, and explicit routing)."""

import pytest
import httpx
from ai.factory import DEFAULT_GEMINI_MODEL_DEFINITIONS
from ai.providers.gemini import GeminiProvider
from ai.providers.router import ModelRouter, NoSuitableModelError
from ai.registry.model_registry import ModelDefinition, ModelRegistry
from ai.registry.provider_registry import ProviderRegistry
from ai.router.tasks import TaskType
from ai.schemas import ModelCapability


@pytest.fixture
def configured_router():
    """Setup router with populated registries."""
    model_reg = ModelRegistry()
    for m in DEFAULT_GEMINI_MODEL_DEFINITIONS:
        model_reg.register(m)

    prov_reg = ProviderRegistry()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://generativelanguage.googleapis.com/v1beta/openai")
    gemini_provider = GeminiProvider(api_key="test-key", client=client)
    prov_reg.register_all_in_one(gemini_provider)

    return ModelRouter(model_registry=model_reg, provider_registry=prov_reg)


def test_explicit_model_override(configured_router):
    """Explicit model selection takes precedence over automatic routing."""
    model_def, provider = configured_router.select_model_and_provider(
        requested_model="gemini-2.0-flash",
        task="fast_text_generation",
    )
    assert model_def.model_id == "gemini-2.0-flash"
    assert provider.name == "gemini"


def test_task_routing_deep_reasoning(configured_router):
    """Deep reasoning task routes to a reasoning model with high priority."""
    model_def, provider = configured_router.select_model_and_provider(
        task=TaskType.DEEP_REASONING,
    )
    assert model_def.model_id in ["gemini-2.0-flash", "gemini-1.5-pro"]
    assert ModelCapability.REASONING in model_def.capabilities


def test_task_routing_fast_text(configured_router):
    """Fast text generation routes to a suitable fast model."""
    model_def, provider = configured_router.select_model_and_provider(
        task="fast text generation",
    )
    assert model_def.model_id in ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-flash"]


def test_task_routing_vision(configured_router):
    """Vision analysis task requires vision support."""
    model_def, provider = configured_router.select_model_and_provider(
        task="vision analysis",
    )
    assert model_def.supports_vision is True
    assert ModelCapability.VISION in model_def.capabilities


def test_task_routing_streaming(configured_router):
    """Streaming task requires streaming support."""
    model_def, provider = configured_router.select_model_and_provider(
        task=TaskType.STREAMING_RESPONSE,
        requires_streaming=True,
    )
    assert model_def.supports_streaming is True


def test_incompatible_capability_raises():
    """Requesting an unsupported capability set raises NoSuitableModelError."""
    model_reg = ModelRegistry()
    # Register model without EMBEDDING
    model_reg.register(
        ModelDefinition(
            model_id="llm-only",
            provider_name="test-prov",
            capabilities={ModelCapability.SUMMARIZATION},
        )
    )
    prov_reg = ProviderRegistry()
    router = ModelRouter(model_registry=model_reg, provider_registry=prov_reg)

    with pytest.raises(NoSuitableModelError):
        router.select_model_and_provider(required_capabilities={ModelCapability.EMBEDDING})
