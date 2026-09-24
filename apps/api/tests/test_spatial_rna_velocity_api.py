"""Integration tests for Spatial RNA Velocity API (Phase 146)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_spatial_rna_velocity_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "tissue_sample": "Developing Hippocampus",
            "developmental_stage": "P0",
            "spot_count": 1200,
            "splicing_rate_gamma": 1.1,
        }
        res = await client.post("/api/v1/spatial-rna-velocity/simulate", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["tissue_sample"] == "Developing Hippocampus"
        assert len(data["spots"]) == 5
        assert len(data["streamlines"]) == 2
