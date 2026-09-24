"""Integration tests for smFRET API (Phase 160)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_smfret_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "biomolecule_name": "API-Hsp90-Test",
            "donor_fluorophore": "Cy3 (Donor)",
            "acceptor_fluorophore": "Cy5 (Acceptor)",
            "laser_power_mw": 15.0,
            "sampling_rate_hz": 100.0,
        }
        res = await client.post("/api/v1/smfret-kinetics/analyze", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["biomolecule_name"] == "API-Hsp90-Test"
        assert len(data["conformational_states"]) == 3
        assert len(data["sample_time_traces"]) == 3
