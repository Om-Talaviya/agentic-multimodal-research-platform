"""Integration tests for CYP450 Metabolism API (Phase 142)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_cyp450_metabolism_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "compound_name": "Warfarin",
            "smiles": "CC(=O)CC(C1=CC=CC=C1)C2=C(C(=O)OC3=CC=CC=C23)O",
            "molecular_weight": 308.33,
            "logp": 2.7,
            "aromatic_ring_count": 3,
            "basic_nitrogen_count": 0,
        }
        res = await client.post("/api/v1/cyp450-metabolism/predict", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["compound_name"] == "Warfarin"
        assert len(data["isoform_predictions"]) == 3
        assert len(data["clearance_curve"]) == 4
