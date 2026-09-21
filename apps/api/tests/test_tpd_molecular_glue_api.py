"""Tests for Phase 121."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_tpd_molecular_glue_api_lifecycle(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"e3_ligase_name": "CRBN", "target_neo_substrate": "GSPT1 (eRF3a)"}
        res = await client.post("/api/v1/tpd-molecular-glue/screen", json=payload, headers=auth_headers)
        assert res.status_code == 201
        sid = res.json()["screen_id"]
        res_get = await client.get(f"/api/v1/tpd-molecular-glue/screens/{sid}", headers=auth_headers)
        assert res_get.status_code == 200
