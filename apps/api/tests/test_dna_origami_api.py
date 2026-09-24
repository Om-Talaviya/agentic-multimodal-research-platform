"""Integration tests for DNA Origami API (Phase 149)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_dna_origami_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "nanorobot_name": "API DNA Origami Box",
            "geometry_type": "Hexagonal Barrel Capsule",
            "target_biomarker": "EGFRvIII",
            "target_cargo_diameter_nm": 8.0,
        }
        res = await client.post("/api/v1/dna-origami/design", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["nanorobot_name"] == "API DNA Origami Box"
        assert len(data["staple_strands"]) >= 3
        assert len(data["latch_mechanisms"]) >= 1
