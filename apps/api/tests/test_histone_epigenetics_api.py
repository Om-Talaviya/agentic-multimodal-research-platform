"""Tests for Phase 112."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_histone_epigenetics_api_lifecycle(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"sample_name": "Jurkat_TCell_H3K27ac", "histone_mark": "H3K27ac", "tissue_or_cell_line": "T-Cell Acute Lymphoblastic Leukemia", "total_peaks": 18500}
        res = await client.post("/api/v1/histone-epigenetics/call-super-enhancers", json=payload, headers=auth_headers)
        assert res.status_code == 201
        sid = res.json()["sample_id"]
        res_get = await client.get(f"/api/v1/histone-epigenetics/samples/{sid}", headers=auth_headers)
        assert res_get.status_code == 200
