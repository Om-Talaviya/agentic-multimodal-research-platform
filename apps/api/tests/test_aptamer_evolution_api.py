"""Integration tests for Aptamer Evolution API (Phase 143)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_aptamer_evolution_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "target_protein_name": "EGFRvIII",
            "aptamer_type": "ssDNA",
            "target_pka": 8.8,
            "selection_rounds": 6,
            "random_region_length": 40,
        }
        res = await client.post("/api/v1/aptamer-evolution/evolve", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["target_protein_name"] == "EGFRvIII"
        assert len(data["evolution_trajectory"]) == 6
        assert data["top_lead"]["kd_nm"] > 0
