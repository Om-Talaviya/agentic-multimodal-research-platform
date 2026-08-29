"""Unit tests for ModelGateway (completion, streaming, vision, fallback, health, telemetry)."""

import json
import pytest
import httpx
from ai.factory import DEFAULT_GEMINI_MODEL_DEFINITIONS
from ai.gateway.model_gateway import ModelGateway
from ai.providers.gemini_web2api import GeminiWeb2APIProvider
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
        "model": "gemini-3.7-flash",
        "choices": [{"index": 0, "message": {"role": "assistant", "content": "Gateway response"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=mock_payload)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://127.0.0.1:8081/v1")
    gemini_provider = GeminiWeb2APIProvider(client=client)

    model_reg = ModelRegistry()
    for m in DEFAULT_GEMINI_MODEL_DEFINITIONS:
        model_reg.register(m)

    prov_reg = ProviderRegistry()
    prov_reg.register_all_in_one(gemini_provider)

    router = ModelRouter(model_registry=model_reg, provider_registry=prov_reg)
    gateway = ModelGateway(router=router, model_registry=model_reg, provider_registry=prov_reg)

    request = LLMRequest(
        messages=[LLMMessage(role=MessageRole.USER, content="Hello Gateway")],
        model="gemini-3.7-flash",
    )

    response = await gateway.complete(request, task="fast text generation")

    assert response.content == "Gateway response"
    assert response.model == "gemini-3.7-flash"
    assert response.metadata["provider"] == "gemini-web2api"
    assert response.metadata["fallback_occurred"] is False
    assert "telemetry" in response.metadata
    assert response.metadata["telemetry"]["latency_ms"] >= 0
    assert response.metadata["telemetry"]["requested_model"] == "gemini-3.7-flash"


@pytest.mark.asyncio
async def test_gateway_fallback_on_failure():
    """Test safe fallback when primary model/provider fails."""
    # Setup two mock providers: Primary (which fails) and Secondary (which succeeds)
    def primary_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Primary bridge down")

    def secondary_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": "cmpl-secondary",
                "model": "secondary-model",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": "Fallback response"}}],
            },
        )

    client_primary = httpx.AsyncClient(transport=httpx.MockTransport(primary_handler), base_url="http://127.0.0.1:8081/v1")
    client_secondary = httpx.AsyncClient(transport=httpx.MockTransport(secondary_handler), base_url="http://127.0.0.1:8082/v1")

    p1 = GeminiWeb2APIProvider(client=client_primary, max_retries=0)
    p1._name = "primary-provider"

    p2 = GeminiWeb2APIProvider(client=client_secondary, max_retries=0)
    p2._name = "secondary-provider"

    model_reg = ModelRegistry()
    model_reg.register(
        ModelDefinition(
            model_id="primary-model",
            provider_name="primary-provider",
            capabilities={ModelCapability.REASONING},
            priority=10,
        )
    )
    model_reg.register(
        ModelDefinition(
            model_id="secondary-model",
            provider_name="secondary-provider",
            capabilities={ModelCapability.REASONING},
            priority=8,
        )
    )

    prov_reg = ProviderRegistry()
    prov_reg.register_llm(p1)
    prov_reg.register_llm(p2)

    router = ModelRouter(model_registry=model_reg, provider_registry=prov_reg)
    gateway = ModelGateway(router=router, model_registry=model_reg, provider_registry=prov_reg, max_fallback_attempts=1)

    req = LLMRequest(messages=[LLMMessage(role=MessageRole.USER, content="Test")])
    res = await gateway.complete(req, fallback_enabled=True)

    assert res.content == "Fallback response"
    assert res.metadata["fallback_occurred"] is True
    assert res.metadata["original_model"] == "primary-model"
    assert res.metadata["actual_model"] == "secondary-model"
    assert res.metadata["provider"] == "secondary-provider"


@pytest.mark.asyncio
async def test_gateway_stream_complete():
    """Test streaming completion through gateway."""
    sse_data = b'data: {"choices":[{"delta":{"content":"Hi"}}]}\n\ndata: [DONE]\n\n'

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"Content-Type": "text/event-stream"}, content=sse_data)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://127.0.0.1:8081/v1")
    gemini = GeminiWeb2APIProvider(client=client)

    model_reg = ModelRegistry()
    for m in DEFAULT_GEMINI_MODEL_DEFINITIONS:
        model_reg.register(m)

    prov_reg = ProviderRegistry()
    prov_reg.register_all_in_one(gemini)

    router = ModelRouter(model_registry=model_reg, provider_registry=prov_reg)
    gateway = ModelGateway(router=router, model_registry=model_reg, provider_registry=prov_reg)

    tokens = []
    async for token in gateway.stream_complete(
        LLMRequest(messages=[LLMMessage(role=MessageRole.USER, content="Stream")])
    ):
        tokens.append(token)

    assert "".join(tokens) == "Hi"


@pytest.mark.asyncio
async def test_gateway_vision_analysis():
    """Test vision analysis through gateway."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "model": "gemini-3.7-flash",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": "Diagram description"}}],
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://127.0.0.1:8081/v1")
    gemini = GeminiWeb2APIProvider(client=client)

    model_reg = ModelRegistry()
    for m in DEFAULT_GEMINI_MODEL_DEFINITIONS:
        model_reg.register(m)

    prov_reg = ProviderRegistry()
    prov_reg.register_all_in_one(gemini)

    router = ModelRouter(model_registry=model_reg, provider_registry=prov_reg)
    gateway = ModelGateway(router=router, model_registry=model_reg, provider_registry=prov_reg)

    res = await gateway.analyze_vision(
        VisionRequest(prompt="Analyze", images=["data:image/png;base64,123"])
    )
    assert res.content == "Diagram description"
    assert res.metadata["telemetry"]["provider"] == "gemini-web2api"


@pytest.mark.asyncio
async def test_gateway_health():
    """Test gateway health aggregation."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"object": "list", "data": [{"id": "gemini-3.7-flash"}]})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://127.0.0.1:8081/v1")
    gemini = GeminiWeb2APIProvider(client=client)

    model_reg = ModelRegistry()
    for m in DEFAULT_GEMINI_MODEL_DEFINITIONS:
        model_reg.register(m)

    prov_reg = ProviderRegistry()
    prov_reg.register_all_in_one(gemini)

    router = ModelRouter(model_registry=model_reg, provider_registry=prov_reg)
    gateway = ModelGateway(router=router, model_registry=model_reg, provider_registry=prov_reg)

    health = await gateway.health_check()
    assert health.healthy is True
    assert health.total_models == len(DEFAULT_GEMINI_MODEL_DEFINITIONS)
    assert "gemini-web2api" in health.active_providers
