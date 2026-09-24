"""Integration tests for Milestone v1.9 API (Phase 161)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_milestone_v1_9_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "cohort_study_name": "API-Pan-Cancer-Cohort",
            "patient_cohort_size": 10000,
            "active_phases_count": 161,
        }
        res = await client.post("/api/v1/milestone-v1-9/stratify", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total_phases_integrated"] == 161
        assert len(data["clusters"]) == 4
        assert len(data["efficacy_matrix"]) == 4
