"""Tests for Phase 119."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_ddr_pathways_api_lifecycle(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"cancer_type": "High-Grade Serous Ovarian Cancer", "primary_ddr_defect": "BRCA1 Germline Truncation", "hrd_genomic_scar_score": 64.0}
        res = await client.post("/api/v1/ddr-pathways/model-vulnerabilities", json=payload, headers=auth_headers)
        assert res.status_code == 201
        pid = res.json()["profile_id"]
        res_get = await client.get(f"/api/v1/ddr-pathways/profiles/{pid}", headers=auth_headers)
        assert res_get.status_code == 200
