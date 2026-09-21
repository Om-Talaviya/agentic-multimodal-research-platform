"""Tests for Phase 118."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_pmhc_class2_api_lifecycle(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"hla_class2_allele": "HLA-DRB1*04:01", "source_protein_antigen": "NY-ESO-1"}
        res = await client.post("/api/v1/pmhc-class2/predict-neoepitopes", json=payload, headers=auth_headers)
        assert res.status_code == 201
        sid = res.json()["screen_id"]
        res_get = await client.get(f"/api/v1/pmhc-class2/screens/{sid}", headers=auth_headers)
        assert res_get.status_code == 200
