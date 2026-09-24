"""Integration tests for Capsid Assembly API (Phase 151)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_capsid_assembly_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "serotype_name": "API-AAV9-Engineered",
            "ph_condition": 7.4,
            "temperature_celsius": 37.0,
            "vp1_vp2_vp3_ratio": "1:1:10",
        }
        res = await client.post("/api/v1/capsid-assembly/simulate", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["serotype_name"] == "API-AAV9-Engineered"
        assert len(data["interfaces"]) == 3
        assert len(data["trajectories"]) == 4
