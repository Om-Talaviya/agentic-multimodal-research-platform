"""Tests for Phase 113."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_tce_bispecific_api_lifecycle(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"construct_name": "Anti-HER2xCD3_BiTE_v2", "tumor_target_antigen": "HER2 (ErbB2)", "format_geometry": "BiTE (scFv-scFv)", "linker_length_aa": 15}
        res = await client.post("/api/v1/tce-bispecific/optimize", json=payload, headers=auth_headers)
        assert res.status_code == 201
        cid = res.json()["construct_id"]
        res_get = await client.get(f"/api/v1/tce-bispecific/constructs/{cid}", headers=auth_headers)
        assert res_get.status_code == 200
