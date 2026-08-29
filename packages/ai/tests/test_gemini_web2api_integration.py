"""Integration test against local Gemini Web2API service.

Sends "Reply with exactly: GEMINI WEB2API INTEGRATION WORKS" using "gemini-3.7-flash".
"""

import pytest
import httpx
from ai.providers.gemini_web2api import GeminiWeb2APIProvider
from ai.schemas import LLMMessage, LLMRequest, MessageRole


def is_gemini_web2api_available() -> bool:
    """Check if the local Gemini Web2API endpoint is responsive."""
    try:
        r = httpx.get("http://127.0.0.1:8081/v1/models", timeout=2.0)
        return r.status_code == 200
    except Exception:
        return False


@pytest.mark.asyncio
async def test_live_gemini_web2api_integration():
    """Live integration test against http://127.0.0.1:8081/v1."""
    if not is_gemini_web2api_available():
        pytest.skip("Gemini Web2API service is not running at http://127.0.0.1:8081/v1")

    provider = GeminiWeb2APIProvider(
        base_url="http://127.0.0.1:8081/v1",
        default_model="gemini-3.7-flash",
    )

    try:
        # Check health
        health = await provider.health_check()
        assert health.healthy is True
        assert "gemini-3.7-flash" in [m.name for m in health.models]

        # Send integration test prompt
        request = LLMRequest(
            messages=[
                LLMMessage(
                    role=MessageRole.USER,
                    content="Reply with exactly: GEMINI WEB2API INTEGRATION WORKS",
                )
            ],
            model="gemini-3.7-flash",
            temperature=0.0,
        )

        response = await provider.complete(request)

        assert response is not None
        assert response.model == "gemini-3.7-flash"
        assert "GEMINI WEB2API INTEGRATION WORKS" in response.content.strip()
    finally:
        await provider.close()
