"""Tests for Phase 115."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_mirna_regulation_api_lifecycle(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"mirna_id": "hsa-miR-21-5p", "seed_sequence": "AGCUUAU", "disease_context": "Glioblastoma Multiforme"}
        res = await client.post("/api/v1/mirna-regulation/model-network", json=payload, headers=auth_headers)
        assert res.status_code == 201
        nid = res.json()["network_id"]
        res_get = await client.get(f"/api/v1/mirna-regulation/networks/{nid}", headers=auth_headers)
        assert res_get.status_code == 200
