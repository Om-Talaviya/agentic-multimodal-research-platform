"""Tests for Phase 117."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_cryo_manifold_api_lifecycle(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"target_complex_name": "Spliceosome C Complex", "total_particles": 145000, "latent_dimensions": 10}
        res = await client.post("/api/v1/cryo-manifold/embed", json=payload, headers=auth_headers)
        assert res.status_code == 201
        did = res.json()["dataset_id"]
        res_get = await client.get(f"/api/v1/cryo-manifold/datasets/{did}", headers=auth_headers)
        assert res_get.status_code == 200
