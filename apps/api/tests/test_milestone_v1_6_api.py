"""Tests for Phase 125."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_milestone_v1_6_api_lifecycle(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"milestone_name": "Milestone v1.6 Centennial Frontier"}
        res = await client.post("/api/v1/milestone-v1-6/verify-platform", json=payload, headers=auth_headers)
        assert res.status_code == 201
        mid = res.json()["milestone_id"]
        res_get = await client.get(f"/api/v1/milestone-v1-6/records/{mid}", headers=auth_headers)
        assert res_get.status_code == 200
        assert res_get.json()["total_phases"] == 125
