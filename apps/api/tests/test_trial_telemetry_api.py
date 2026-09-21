"""Tests for Phase 122."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_trial_telemetry_api_lifecycle(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"protocol_number": "PROTO-ONC-2026-09", "total_subjects": 150}
        res = await client.post("/api/v1/trial-telemetry/scan-anomalies", json=payload, headers=auth_headers)
        assert res.status_code == 201
        cid = res.json()["cohort_id"]
        res_get = await client.get(f"/api/v1/trial-telemetry/cohorts/{cid}", headers=auth_headers)
        assert res_get.status_code == 200
