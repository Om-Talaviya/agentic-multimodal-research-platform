"""Unit tests for official GeminiProvider using mocked HTTP transport."""

import pytest
import httpx
from ai.providers.gemini import GeminiProvider, SUPPORTED_GEMINI_MODELS
from ai.schemas import (
    LLMMessage,
    LLMRequest,
    MessageRole,
    ModelCapability,
    VisionRequest,
)
from shared.exceptions import ModelNotFoundError, ProviderError, ProviderUnavailableError


@pytest.mark.asyncio
async def test_gemini_provider_protocol_conformance():
    """Verify GeminiProvider adheres to LLMProvider and VisionProvider protocols."""
    provider = GeminiProvider(api_key="test-key", base_url="https://generativelanguage.googleapis.com/v1beta/openai")

    assert provider.name == "gemini"
    assert provider.is_local is False
    assert ModelCapability.REASONING in provider.capabilities
    assert ModelCapability.VISION in provider.capabilities
    assert len(provider.models) == len(SUPPORTED_GEMINI_MODELS)


@pytest.mark.asyncio
async def test_gemini_provider_chat_mock():
    """Test GeminiProvider chat completions parsing and response structure."""
    def mock_handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/chat/completions")

        payload = {
            "id": "chatcmpl-test-001",
            "object": "chat.completion",
            "created": 1710000000,
            "model": "gemini-2.0-flash",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "GEMINI OFFICIAL API WORKS"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 15,
                "completion_tokens": 10,
                "total_tokens": 25,
            },
        }
        return httpx.Response(200, json=payload)

    transport = httpx.MockTransport(mock_handler)
    client = httpx.AsyncClient(transport=transport, base_url="https://generativelanguage.googleapis.com/v1beta/openai")

    provider = GeminiProvider(api_key="test-key", client=client)

    req = LLMRequest(
        messages=[LLMMessage(role=MessageRole.USER, content="Hello Gemini")],
        model="gemini-2.0-flash",
        temperature=0.7,
    )

    response = await provider.complete(req)

    assert response.content == "GEMINI OFFICIAL API WORKS"
    assert response.model == "gemini-2.0-flash"
    assert response.usage["total_tokens"] == 25
    assert response.metadata["provider"] == "gemini"
    assert response.metadata["latency_ms"] > 0


@pytest.mark.asyncio
async def test_gemini_provider_chat_stream_mock():
    """Test GeminiProvider streaming generator."""
    def mock_handler(request: httpx.Request) -> httpx.Response:
        content = (
            'data: {"choices":[{"delta":{"content":"Hello"}}]}\n\n'
            'data: {"choices":[{"delta":{"content":" World"}}]}\n\n'
            'data: [DONE]\n\n'
        )
        return httpx.Response(200, text=content)

    transport = httpx.MockTransport(mock_handler)
    client = httpx.AsyncClient(transport=transport, base_url="https://generativelanguage.googleapis.com/v1beta/openai")

    provider = GeminiProvider(api_key="test-key", client=client)

    req = LLMRequest(
        messages=[LLMMessage(role=MessageRole.USER, content="Stream hello")],
        model="gemini-2.0-flash",
    )

    chunks = []
    async for chunk in provider.stream_complete(req):
        chunks.append(chunk)

    assert "".join(chunks) == "Hello World"


@pytest.mark.asyncio
async def test_gemini_provider_vision_analysis_mock():
    """Test GeminiProvider multimodal vision image analysis."""
    def mock_handler(request: httpx.Request) -> httpx.Response:
        payload = {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "A high-resolution scientific diagram.",
                    }
                }
            ]
        }
        return httpx.Response(200, json=payload)

    transport = httpx.MockTransport(mock_handler)
    client = httpx.AsyncClient(transport=transport, base_url="https://generativelanguage.googleapis.com/v1beta/openai")

    provider = GeminiProvider(api_key="test-key", client=client)

    req = VisionRequest(
        images=["aGVsbG8="],
        prompt="Describe diagram",
        model="gemini-2.0-flash",
    )

    response = await provider.analyze(req)
    assert "scientific diagram" in response.content
    assert response.model == "gemini-2.0-flash"
    assert response.metadata["provider"] == "gemini"


@pytest.mark.asyncio
async def test_gemini_provider_error_handling():
    """Test error handling for 404, 500, and connection errors."""
    def mock_handler(request: httpx.Request) -> httpx.Response:
        if "404" in str(request.url):
            return httpx.Response(404, text="Model not found")
        return httpx.Response(500, text="Internal Server Error")

    transport = httpx.MockTransport(mock_handler)
    client = httpx.AsyncClient(transport=transport, base_url="https://generativelanguage.googleapis.com/v1beta/openai")

    provider = GeminiProvider(api_key="test-key", client=client)

    with pytest.raises(ProviderError):
        await provider.complete(LLMRequest(messages=[LLMMessage(role=MessageRole.USER, content="hi")]))
