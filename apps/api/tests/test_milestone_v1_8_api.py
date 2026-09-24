"""Integration tests for Milestone v1.8 API (Phase 154)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_milestone_v1_8_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "orchestration_name": "API Milestone v1.8 Test",
            "target_indication": "Immuno-Oncology",
            "active_phases_count": 154,
        }
        res = await client.post("/api/v1/milestone-v1-8/synthesize", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total_phases_integrated"] == 154
        assert len(data["workflow_nodes"]) == 8
        assert len(data["executive_reports"]) == 1
