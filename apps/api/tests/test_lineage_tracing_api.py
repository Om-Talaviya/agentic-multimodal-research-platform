"""Tests for Phase 114."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_lineage_tracing_api_lifecycle(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"experiment_title": "Chemotherapy Resistance Clonal Evolution", "barcoding_technology": "CRISPR-Cas9 Scarring (GESTALT)", "total_clones": 850, "selection_pressure": "Cisplatin 10uM Selection"}
        res = await client.post("/api/v1/lineage-tracing/simulate", json=payload, headers=auth_headers)
        assert res.status_code == 201
        eid = res.json()["experiment_id"]
        res_get = await client.get(f"/api/v1/lineage-tracing/experiments/{eid}", headers=auth_headers)
        assert res_get.status_code == 200
