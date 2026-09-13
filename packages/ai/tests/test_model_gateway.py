"""Unit tests for ModelGateway (completion, streaming, vision, fallback, health, telemetry)."""

import json
import pytest
import httpx
from ai.factory import DEFAULT_GEMINI_MODEL_DEFINITIONS
from ai.gateway.model_gateway import ModelGateway
from ai.providers.gemini import GeminiProvider
from ai.providers.router import ModelRouter
from ai.registry.model_registry import ModelDefinition, ModelRegistry
from ai.registry.provider_registry import ProviderRegistry
from ai.schemas import (
    LLMMessage,
    LLMRequest,
    MessageRole,
    ModelCapability,
    VisionRequest,
)
from shared.exceptions import ProviderUnavailableError


@pytest.mark.asyncio
async def test_gateway_complete_success():
    """Test gateway completion, normalization, and telemetry."""
    mock_payload = {
        "id": "cmpl-gateway-123",
        "model": "gemini-2.0-flash",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": "Gateway response"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=mock_payload)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://generativelanguage.googleapis.com/v1beta/openai")
    gemini_provider = GeminiProvider(api_key="test-key", client=client)

    model_reg = ModelRegistry()
    for m in DEFAULT_GEMINI_MODEL_DEFINITIONS:
        model_reg.register(m)

    prov_reg = ProviderRegistry()
    prov_reg.register_all_in_one(gemini_provider)

    router = ModelRouter(model_registry=model_reg, provider_registry=prov_reg)
    gateway = ModelGateway(router=router, model_registry=model_reg, provider_registry=prov_reg)

    request = LLMRequest(
        messages=[LLMMessage(role=MessageRole.USER, content="Hello Gateway")],
        model="gemini-2.0-flash",
    )

    response = await gateway.complete(request, task="fast text generation")

    assert response.content == "Gateway response"
    assert response.model == "gemini-2.0-flash"
    assert response.metadata["provider"] == "gemini"
    assert response.metadata["fallback_occurred"] is False
    assert "telemetry" in response.metadata
    assert response.metadata["telemetry"]["latency_ms"] >= 0


@pytest.mark.asyncio
async def test_gateway_complete_with_fallback():
    """Test automatic failover to fallback model when primary provider fails."""
    def primary_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Primary failed")

    def secondary_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={
            "id": "cmpl-sec",
            "model": "gemini-1.5-flash",
            "choices": [{"message": {"content": "Fallback response"}}],
            "usage": {"total_tokens": 8},
        })

    client_primary = httpx.AsyncClient(transport=httpx.MockTransport(primary_handler), base_url="https://primary.ai/v1")
    client_secondary = httpx.AsyncClient(transport=httpx.MockTransport(secondary_handler), base_url="https://secondary.ai/v1")

    p1 = GeminiProvider(api_key="key1", client=client_primary, max_retries=0, name="p1")
    p2 = GeminiProvider(api_key="key2", client=client_secondary, max_retries=0, name="p2")

    model_reg = ModelRegistry()
    m1 = ModelDefinition(
        model_id="gemini-2.0-flash",
        provider_name="p1",
        capabilities={ModelCapability.REASONING},
        priority=10,
    )
    m2 = ModelDefinition(
        model_id="gemini-1.5-flash",
        provider_name="p2",
        capabilities={ModelCapability.REASONING},
        priority=5,
    )
    model_reg.register(m1)
    model_reg.register(m2)

    prov_reg = ProviderRegistry()
    prov_reg.register_llm(p1)
    prov_reg.register_llm(p2)

    router = ModelRouter(model_registry=model_reg, provider_registry=prov_reg)
    gateway = ModelGateway(router=router, model_registry=model_reg, provider_registry=prov_reg)

    request = LLMRequest(messages=[LLMMessage(role=MessageRole.USER, content="Hello")])
    response = await gateway.complete(request, task="reasoning")

    assert response.content == "Fallback response"
    assert response.model == "gemini-1.5-flash"
    assert response.metadata["fallback_occurred"] is True
    assert "primary_error" in response.metadata


@pytest.mark.asyncio
async def test_gateway_stream_success():
    """Test streaming chunk forwarding."""
    def handler(request: httpx.Request) -> httpx.Response:
        content = 'data: {"choices":[{"delta":{"content":"A"}}]}\n\ndata: {"choices":[{"delta":{"content":"B"}}]}\n\ndata: [DONE]\n\n'
        return httpx.Response(200, text=content)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://generativelanguage.googleapis.com/v1beta/openai")
    gemini = GeminiProvider(api_key="test-key", client=client)

    model_reg = ModelRegistry()
    for m in DEFAULT_GEMINI_MODEL_DEFINITIONS:
        model_reg.register(m)

    prov_reg = ProviderRegistry()
    prov_reg.register_all_in_one(gemini)

    router = ModelRouter(model_registry=model_reg, provider_registry=prov_reg)
    gateway = ModelGateway(router=router, model_registry=model_reg, provider_registry=prov_reg)

    request = LLMRequest(messages=[LLMMessage(role=MessageRole.USER, content="Stream")])
    chunks = []
    async for chunk in gateway.stream_complete(request):
        chunks.append(chunk)

    assert "".join(chunks) == "AB"


@pytest.mark.asyncio
async def test_gateway_vision_analysis():
    """Test multimodal vision analysis route."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={
            "choices": [{"message": {"content": "Image analysis text"}}],
        })

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://generativelanguage.googleapis.com/v1beta/openai")
    gemini = GeminiProvider(api_key="test-key", client=client)

    model_reg = ModelRegistry()
    for m in DEFAULT_GEMINI_MODEL_DEFINITIONS:
        model_reg.register(m)

    prov_reg = ProviderRegistry()
    prov_reg.register_all_in_one(gemini)

    router = ModelRouter(model_registry=model_reg, provider_registry=prov_reg)
    gateway = ModelGateway(router=router, model_registry=model_reg, provider_registry=prov_reg)

    vreq = VisionRequest(images=["aGVsbG8="], prompt="Describe", model="gemini-2.0-flash")
    res = await gateway.analyze_vision(vreq)

    assert res.content == "Image analysis text"
    assert res.metadata["telemetry"]["provider"] == "gemini"


@pytest.mark.asyncio
async def test_gateway_health_check():
    """Test unified health check across all registered providers."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": [{"id": "gemini-2.0-flash"}]})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://generativelanguage.googleapis.com/v1beta/openai")
    gemini = GeminiProvider(api_key="test-key", client=client)

    model_reg = ModelRegistry()
    prov_reg = ProviderRegistry()
    prov_reg.register_all_in_one(gemini)

    router = ModelRouter(model_registry=model_reg, provider_registry=prov_reg)
    gateway = ModelGateway(router=router, model_registry=model_reg, provider_registry=prov_reg)

    health = await gateway.health_check()
    assert health.healthy is True
    assert "gemini" in health.active_providers
