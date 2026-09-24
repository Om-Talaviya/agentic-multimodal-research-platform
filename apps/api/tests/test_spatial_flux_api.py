"""Integration tests for Spatial Flux API (Phase 150)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_spatial_flux_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "tissue_sample_id": "API-TME-Test",
            "organ_context": "Colorectal Carcinoma",
            "single_cells_count": 2000,
            "perfusion_radius_um": 250.0,
        }
        res = await client.post("/api/v1/spatial-flux/solve", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["tissue_sample_id"] == "API-TME-Test"
        assert len(data["pathway_fluxes"]) >= 4
        assert len(data["microdomains"]) >= 3
