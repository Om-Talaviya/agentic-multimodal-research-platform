"""Integration tests for Spatial Proteomics CODEX API (Phase 155)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_spatial_proteomics_codex_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "tissue_sample_name": "API-CODEX-Test",
            "organ_tissue_type": "Melanoma Biopsy",
            "panel_plex_level": 40,
            "single_cells_estimate": 8500,
        }
        res = await client.post("/api/v1/spatial-proteomics-codex/process", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["tissue_sample_name"] == "API-CODEX-Test"
        assert len(data["marker_expressions"]) >= 5
        assert len(data["neighborhood_phenotypes"]) >= 3
