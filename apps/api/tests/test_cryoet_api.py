"""Tests for Cryo-ET Subtomogram Averaging API endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.src.api.main import app


@pytest.mark.asyncio
async def test_cryoet_api_endpoints(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Reconstruct Dataset
        payload = {
            "sample_name": "In-Situ 80S Ribosome",
            "specimen_organism": "S. cerevisiae",
            "cellular_compartment": "CYTOSOL",
            "tilt_angle_min": -60.0,
            "tilt_angle_max": 60.0,
            "total_tilt_images": 41,
            "pixel_size_angstrom": 1.35,
            "nominal_defocus_um": -2.5
        }
        res = await client.post("/api/v1/cryoet/datasets/reconstruct", json=payload, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert "id" in data
        assert data["sample_name"] == "In-Situ 80S Ribosome"
        assert "refinement" in data
        assert data["refinement"]["estimated_resolution_angstrom"] > 0
        dataset_id = data["id"]

        # 2. List Datasets
        res_list = await client.get("/api/v1/cryoet/datasets", headers=auth_headers)
        assert res_list.status_code == 200
        datasets = res_list.json()
        assert len(datasets) >= 1

        # 3. Get Dataset Details
        res_get = await client.get(f"/api/v1/cryoet/datasets/{dataset_id}", headers=auth_headers)
        assert res_get.status_code == 200
        details = res_get.json()
        assert details["id"] == dataset_id
        assert len(details["particles"]) >= 1
        assert len(details["refinements"]) >= 1
