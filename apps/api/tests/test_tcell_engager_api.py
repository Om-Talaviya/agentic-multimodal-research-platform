"""Integration tests for T-Cell Engager API (Phase 158)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_tcell_engager_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "construct_name": "API-TriTE-Test",
            "modality_format": "TriTE",
            "primary_tumor_antigen": "GPC3 / Claudin18.2",
            "cd3_arm_affinity_nM": 10.0,
        }
        res = await client.post("/api/v1/tcell-engager/model-geometry", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["construct_name"] == "API-TriTE-Test"
        assert len(data["binding_domains"]) == 3
        assert len(data["synapse_profiles"]) == 3
