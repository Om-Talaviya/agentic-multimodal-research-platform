"""Tests for Phase 111."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_ctc_metastasis_api_lifecycle(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"patient_id": "PT-MET-8841", "primary_tumor_type": "Triple-Negative Breast Cancer", "ctc_count": 22, "epcam_expression": 1.2, "vimentin_expression": 3.8}
        res = await client.post("/api/v1/ctc-metastasis/analyze", json=payload, headers=auth_headers)
        assert res.status_code == 201
        sid = res.json()["sample_id"]
        res_get = await client.get(f"/api/v1/ctc-metastasis/samples/{sid}", headers=auth_headers)
        assert res_get.status_code == 200
