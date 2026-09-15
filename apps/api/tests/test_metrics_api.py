"""Integration tests for Prometheus metrics API endpoint."""

import httpx
import pytest
from main import app


from unittest.mock import AsyncMock, MagicMock
from api.dependencies import get_model_router


@pytest.mark.asyncio
async def test_metrics_endpoint():
    mock_router = MagicMock()
    mock_router.health_check_all = AsyncMock(return_value={"gemini": MagicMock(healthy=True, error=None)})
    app.dependency_overrides[get_model_router] = lambda: mock_router

    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            # Perform a health check request to generate metric activity
            await client.get("/api/v1/health")

            # Fetch /metrics
            resp = await client.get("/metrics")
            assert resp.status_code == 200
            assert "text/plain" in resp.headers["content-type"]
            text = resp.text

            assert "http_requests_total" in text
            assert "http_request_duration_seconds" in text
            assert "active_requests" in text

            # Also verify /api/v1/metrics
            api_metrics_resp = await client.get("/api/v1/metrics")
            assert api_metrics_resp.status_code == 200
    finally:
        app.dependency_overrides.pop(get_model_router, None)
