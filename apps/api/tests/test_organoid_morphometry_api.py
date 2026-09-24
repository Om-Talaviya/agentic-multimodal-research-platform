"""Integration tests for Organoid Morphometry API (Phase 147)."""

import pytest
from httpx import ASGITransport, AsyncClient
from main import app


@pytest.mark.asyncio
async def test_organoid_morphometry_api(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "study_name": "API Organoid Test",
            "tumor_type": "Glioblastoma Multiforme",
            "z_slices_count": 5,
            "primary_compound": "Temozolomide",
            "compound_dose_uM": 10.0,
        }
        res = await client.post("/api/v1/organoid-morphometry/analyze", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["study_name"] == "API Organoid Test"
        assert len(data["z_slices"]) == 5
        assert len(data["dose_responses"]) == 1
