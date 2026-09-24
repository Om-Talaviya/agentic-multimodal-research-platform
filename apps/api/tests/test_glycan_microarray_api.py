"""Integration tests for Glycan Microarray API (Phase 148)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_glycan_microarray_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "target_lectin_name": "Galectin-3",
            "organism_source": "Homo sapiens",
            "concentration_ug_ml": 10.0,
        }
        res = await client.post("/api/v1/glycan-microarray/screen", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["target_lectin_name"] == "Galectin-3"
        assert len(data["top_binding_spots"]) == 5
        assert len(data["motif_enrichments"]) == 3
