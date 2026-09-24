"""Integration tests for CFPS TX-TL API (Phase 157)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_cfps_txtl_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "target_protein_name": "API-GFP-Test",
            "extract_system_type": "E. coli BL21 Star (DE3)",
            "reaction_mode": "CECF",
            "dna_template_concentration_nM": 10.0,
            "reaction_temperature_celsius": 30.0,
        }
        res = await client.post("/api/v1/cfps-txtl/simulate", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["target_protein_name"] == "API-GFP-Test"
        assert len(data["yield_trajectories"]) == 7
        assert len(data["substrate_depletions"]) == 3
