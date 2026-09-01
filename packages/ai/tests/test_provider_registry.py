"""Unit tests for ProviderRegistry."""

import pytest
import httpx
from ai.providers.gemini import GeminiProvider
from ai.registry.provider_registry import ProviderRegistry
from ai.schemas import ModelCapability


@pytest.mark.asyncio
async def test_provider_registry_registration():
    """Test registering and retrieving providers."""
    registry = ProviderRegistry()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": [{"id": "gemini-2.0-flash"}]})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://generativelanguage.googleapis.com/v1beta/openai")
    gemini_provider = GeminiProvider(api_key="test-key", client=client)

    registry.register_all_in_one(gemini_provider)

    assert registry.get_llm("gemini") == gemini_provider
    assert registry.get_vision("gemini") == gemini_provider
    assert registry.get_embedding("gemini") is None
    assert len(registry.list_llm_providers()) == 1
    assert len(registry.list_vision_providers()) == 1


@pytest.mark.asyncio
async def test_provider_registry_health_check_all():
    """Test running health check across all providers."""
    registry = ProviderRegistry()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"object": "list", "data": [{"id": "gemini-2.0-flash"}]})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="https://generativelanguage.googleapis.com/v1beta/openai")
    gemini = GeminiProvider(api_key="test-key", client=client)

    registry.register_llm(gemini)

    health = await registry.health_check_all()
    assert "llm:gemini" in health
    assert health["llm:gemini"].healthy is True
    assert len(health["llm:gemini"].models) >= 1
