"""Integration tests for PROTAC Kinetics API (Phase 156)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_protac_kinetics_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "protac_compound_name": "API-PROTAC-01",
            "target_protein_name": "STAT3",
            "e3_ligase_name": "CRBN",
            "linker_type": "Alkyl Linker",
            "target_kd_binary_nM": 15.0,
            "e3_kd_binary_nM": 30.0,
        }
        res = await client.post("/api/v1/protac-kinetics/simulate", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["protac_compound_name"] == "API-PROTAC-01"
        assert len(data["e3_profiles"]) == 2
        assert len(data["dose_response_curve"]) >= 5
