"""Integration tests for Clinical ePRO API (Phase 141)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_clinical_epro_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "protocol_id": "PH3-IMMUNO-992",
            "therapeutic_area": "Solid Oncology",
            "patient_cohort_size": 50,
            "baseline_qol_score": 0.72,
            "trial_duration_weeks": 24,
        }
        res = await client.post("/api/v1/clinical-epro/simulate", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["protocol_id"] == "PH3-IMMUNO-992"
        assert len(data["active_alerts"]) == 2
