"""Integration tests for Model Optimization and Profile REST endpoints."""
import httpx
import pytest
from main import app


@pytest.mark.asyncio
async def test_get_optimization_profiles():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/models/profiles")
        assert resp.status_code == 200
        data = resp.json()
        assert "balanced" in data
        assert "cost_minimized" in data
        assert "speed_maximized" in data
        assert "quality_maximized" in data
        assert data["balanced"]["quality_weight"] > 0


@pytest.mark.asyncio
async def test_simulate_model_optimization():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "task": "long_form_research",
            "profile": "cost_minimized",
        }
        resp = await client.post("/api/v1/models/optimize", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "selected_model_id" in data
        assert "ranked_candidates" in data
        assert len(data["ranked_candidates"]) > 0
        assert "tradeoff_analysis" in data
        assert "pareto_frontier" in data
