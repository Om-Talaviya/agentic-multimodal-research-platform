"""Unit tests for ProviderRegistry."""

import pytest
import httpx
from ai.providers.gemini_web2api import GeminiWeb2APIProvider
from ai.registry.provider_registry import ProviderRegistry
from ai.schemas import ModelCapability


@pytest.mark.asyncio
async def test_provider_registry_registration():
    """Test registering and retrieving providers."""
    registry = ProviderRegistry()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": [{"id": "gemini-3.7-flash"}]})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://127.0.0.1:8081/v1")
    gemini_provider = GeminiWeb2APIProvider(client=client)

    registry.register_all_in_one(gemini_provider)

    assert registry.get_llm("gemini-web2api") == gemini_provider
    assert registry.get_vision("gemini-web2api") == gemini_provider
    assert registry.get_embedding("gemini-web2api") is None
    assert len(registry.list_llm_providers()) == 1
    assert len(registry.list_vision_providers()) == 1


@pytest.mark.asyncio
async def test_provider_registry_health_check_all():
    """Test running health check across all providers."""
    registry = ProviderRegistry()

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"object": "list", "data": [{"id": "gemini-3.7-flash"}]})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://127.0.0.1:8081/v1")
    gemini = GeminiWeb2APIProvider(client=client)

    registry.register_llm(gemini)

    health = await registry.health_check_all()
    assert "llm:gemini-web2api" in health
    assert health["llm:gemini-web2api"].healthy is True
    assert len(health["llm:gemini-web2api"].models) == 1
