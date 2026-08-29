"""Unit tests for GeminiWeb2APIProvider using mocked HTTP transport."""

import json
import pytest
import httpx
from ai.providers.base import LLMProvider, VisionProvider
from ai.providers.gemini_web2api import GeminiWeb2APIProvider, SUPPORTED_GEMINI_MODELS
from ai.schemas import (
    LLMMessage,
    LLMRequest,
    MessageRole,
    ModelCapability,
    VisionRequest,
)
from shared.exceptions import ModelNotFoundError, ProviderError, ProviderUnavailableError


def test_provider_protocol_compliance():
    """Verify GeminiWeb2APIProvider adheres to LLMProvider and VisionProvider protocols."""
    provider = GeminiWeb2APIProvider(base_url="http://127.0.0.1:8081/v1")
    assert isinstance(provider, LLMProvider)
    assert isinstance(provider, VisionProvider)
    assert provider.name == "gemini-web2api"
    assert provider.is_local is True
    assert ModelCapability.REASONING in provider.capabilities
    assert ModelCapability.VISION in provider.capabilities
    assert "gemini-3.7-flash" in provider.models
    assert len(provider.models) == len(SUPPORTED_GEMINI_MODELS)


@pytest.mark.asyncio
async def test_complete_success():
    """Test successful chat completion and response normalization."""
    mock_payload = {
        "id": "chatcmpl-test-123",
        "object": "chat.completion",
        "created": 1700000000,
        "model": "gemini-3.7-flash",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "GEMINI WEB2API INTEGRATION WORKS"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 6, "total_tokens": 16},
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/v1/chat/completions"
        body = json.loads(request.content.decode("utf-8"))
        assert body["model"] == "gemini-3.7-flash"
        assert body["messages"] == [{"role": "user", "content": "Hello Gemini"}]
        return httpx.Response(200, json=mock_payload)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://127.0.0.1:8081/v1")
    provider = GeminiWeb2APIProvider(base_url="http://127.0.0.1:8081/v1", client=client)

    request = LLMRequest(
        messages=[LLMMessage(role=MessageRole.USER, content="Hello Gemini")],
        model="gemini-3.7-flash",
    )

    response = await provider.complete(request)

    assert response.content == "GEMINI WEB2API INTEGRATION WORKS"
    assert response.model == "gemini-3.7-flash"
    assert response.finish_reason == "stop"
    assert response.usage == {"prompt_tokens": 10, "completion_tokens": 6, "total_tokens": 16}
    assert response.metadata["provider"] == "gemini-web2api"
    assert response.metadata["raw_id"] == "chatcmpl-test-123"


@pytest.mark.asyncio
async def test_model_selection():
    """Test various supported model selections."""
    test_models = [
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.5-flash-thinking",
        "gemini-3.1-pro",
        "gemini-auto",
        "gemini-3.5-flash-thinking-lite",
        "gemini-flash-lite",
    ]

    for model in test_models:
        def handler(req: httpx.Request) -> httpx.Response:
            body = json.loads(req.content.decode("utf-8"))
            return httpx.Response(
                200,
                json={
                    "id": "cmpl",
                    "model": body["model"],
                    "choices": [{"index": 0, "message": {"role": "assistant", "content": f"Reply from {body['model']}"}}],
                },
            )

        client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://127.0.0.1:8081/v1")
        provider = GeminiWeb2APIProvider(client=client)
        res = await provider.complete(
            LLMRequest(
                messages=[LLMMessage(role=MessageRole.USER, content="Test")],
                model=model,
            )
        )
        assert res.model == model
        assert res.content == f"Reply from {model}"


@pytest.mark.asyncio
async def test_stream_complete():
    """Test streaming completion token yielding."""
    sse_chunks = [
        b'data: {"id":"1","choices":[{"delta":{"content":"Hello"}}]}\n\n',
        b'data: {"id":"1","choices":[{"delta":{"content":" World"}}]}\n\n',
        b'data: [DONE]\n\n',
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            headers={"Content-Type": "text/event-stream"},
            content=b"".join(sse_chunks),
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://127.0.0.1:8081/v1")
    provider = GeminiWeb2APIProvider(client=client)

    collected = []
    async for chunk in provider.stream_complete(
        LLMRequest(messages=[LLMMessage(role=MessageRole.USER, content="Stream test")])
    ):
        collected.append(chunk)

    assert "".join(collected) == "Hello World"
    await provider.close()


@pytest.mark.asyncio
async def test_analyze_vision():
    """Test vision analysis request and normalization."""
    mock_payload = {
        "id": "vision-123",
        "model": "gemini-3.7-flash",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "The image shows a chart."},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 100, "completion_tokens": 10},
    }

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content.decode("utf-8"))
        assert len(body["messages"]) == 1
        user_msg = body["messages"][0]
        assert user_msg["role"] == "user"
        assert user_msg["content"][0]["type"] == "text"
        assert user_msg["content"][1]["type"] == "image_url"
        return httpx.Response(200, json=mock_payload)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://127.0.0.1:8081/v1")
    provider = GeminiWeb2APIProvider(client=client)

    res = await provider.analyze(
        VisionRequest(
            prompt="Analyze this chart",
            images=["data:image/png;base64,iVBORw0KGgoAAAANSUhEUg=="],
            model="gemini-3.7-flash",
        )
    )

    assert res.content == "The image shows a chart."
    assert res.model == "gemini-3.7-flash"
    assert res.usage["completion_tokens"] == 10


@pytest.mark.asyncio
async def test_unknown_model_error():
    """Test that requesting an unknown model raises ModelNotFoundError."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": {"message": "Unknown model: invalid-model"}})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://127.0.0.1:8081/v1")
    provider = GeminiWeb2APIProvider(client=client, max_retries=0)

    with pytest.raises(ModelNotFoundError) as exc_info:
        await provider.complete(
            LLMRequest(
                messages=[LLMMessage(role=MessageRole.USER, content="Test")],
                model="invalid-model",
            )
        )
    assert "invalid-model" in str(exc_info.value)


@pytest.mark.asyncio
async def test_connection_error_raises_unavailable():
    """Test that connection failure raises ProviderUnavailableError."""
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Failed to connect to 127.0.0.1:8081")

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://127.0.0.1:8081/v1")
    provider = GeminiWeb2APIProvider(client=client, max_retries=1)

    with pytest.raises(ProviderUnavailableError):
        await provider.complete(
            LLMRequest(messages=[LLMMessage(role=MessageRole.USER, content="Hello")])
        )


@pytest.mark.asyncio
async def test_retry_on_server_error():
    """Test retry on transient 502/503 errors."""
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            return httpx.Response(502, text="Bad Gateway")
        return httpx.Response(
            200,
            json={
                "id": "cmpl",
                "model": "gemini-3.7-flash",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": "Recovered!"}}],
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://127.0.0.1:8081/v1")
    provider = GeminiWeb2APIProvider(client=client, max_retries=2)

    res = await provider.complete(
        LLMRequest(messages=[LLMMessage(role=MessageRole.USER, content="Hello")])
    )
    assert attempts == 2
    assert res.content == "Recovered!"


@pytest.mark.asyncio
async def test_router_with_gemini_web2api():
    """Test that ModelRouter routes requests to GeminiWeb2APIProvider based on capabilities."""
    from ai.providers.router import ModelRouter
    from ai.schemas import ModelCapabilities

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": "cmpl-router",
                "model": "gemini-3.7-flash",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": "Routed to Gemini"}}],
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://127.0.0.1:8081/v1")
    gemini_provider = GeminiWeb2APIProvider(client=client)

    router = ModelRouter(
        llm_providers=[gemini_provider],
        vision_providers=[gemini_provider],
        embedding_providers=[],
        reranker_providers=[],
    )

    selected_llm = router.select_llm(ModelCapabilities.for_task("research"), prefer_local=True)
    assert selected_llm.name == "gemini-web2api"

    selected_vision = router.select_vision(prefer_local=True)
    assert selected_vision.name == "gemini-web2api"

    health = await router.health_check_all()
    assert "llm:gemini-web2api" in health
    assert "vision:gemini-web2api" in health


@pytest.mark.asyncio
async def test_health_check_healthy():
    """Test health check when server is responsive."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "object": "list",
                "data": [
                    {"id": "gemini-3.7-flash", "object": "model"},
                    {"id": "gemini-3.6-flash", "object": "model"},
                ],
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://127.0.0.1:8081/v1")
    provider = GeminiWeb2APIProvider(client=client)

    health = await provider.health_check()
    assert health.healthy is True
    assert health.provider == "gemini-web2api"
    assert len(health.models) == 2
    assert health.models[0].name == "gemini-3.7-flash"


@pytest.mark.asyncio
async def test_health_check_unhealthy_no_crash():
    """Test that health check returns healthy=False instead of crashing when service is down."""
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Connection refused")

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://127.0.0.1:8081/v1")
    provider = GeminiWeb2APIProvider(client=client)

    health = await provider.health_check()
    assert health.healthy is False
    assert health.provider == "gemini-web2api"
    assert health.error is not None
