"""Tests for Phase 116."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_spatial_msi_api_lifecycle(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {"tissue_section_name": "Glioblastoma_Tissue_Slice_04", "msi_modality": "MALDI-MSI (FT-ICR)", "spatial_resolution_um": 20.0}
        res = await client.post("/api/v1/spatial-msi/profile-gradients", json=payload, headers=auth_headers)
        assert res.status_code == 201
        sid = res.json()["sample_id"]
        res_get = await client.get(f"/api/v1/spatial-msi/samples/{sid}", headers=auth_headers)
        assert res_get.status_code == 200
