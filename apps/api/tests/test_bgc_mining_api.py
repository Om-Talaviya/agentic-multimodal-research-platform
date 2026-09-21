"""Tests for Phase 123."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_bgc_mining_api_lifecycle(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"organism_species_name": "Streptomyces coelicolor A3(2)", "genome_size_mbp": 8.66}
        res = await client.post("/api/v1/bgc-mining/mine-genome", json=payload, headers=auth_headers)
        assert res.status_code == 201
        gid = res.json()["genome_id"]
        res_get = await client.get(f"/api/v1/bgc-mining/genomes/{gid}", headers=auth_headers)
        assert res_get.status_code == 200
