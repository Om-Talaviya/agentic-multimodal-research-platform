"""Tests for Spatial Proteogenomics API."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_spatial_proteogenomics_api_endpoints(auth_headers: dict) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "study_name": "API Spatial Proteogenomics Test",
            "tissue_sample_id": "GBM_TME_Slice_04",
            "custom_spots": [
                {
                    "spot_barcode": "SPOT_A1_001",
                    "x_coord": 124.5,
                    "y_coord": 450.2,
                    "target_mrna_symbol": "EGFR",
                    "mrna_normalized_count": 48.2,
                    "target_protein_antibody": "Total-EGFR (Clone D38B1)",
                    "protein_adt_signal": 1420.0,
                    "colocalization_pearson_r": 0.91,
                    "subcellular_niche": "Invasive Glioblastoma Core",
                }
            ],
        }
        res = await client.post("/api/v1/spatial-proteogenomics/analyze", json=payload, headers=auth_headers)
        assert res.status_code == 201, res.text
        data = res.json()
        assert data["study_name"] == "API Spatial Proteogenomics Test"
        study_id = data["id"]
        assert len(data["spots"]) == 1

        # List
        res_list = await client.get("/api/v1/spatial-proteogenomics/studies", headers=auth_headers)
        assert res_list.status_code == 200
        assert any(s["id"] == study_id for s in res_list.json())

        # Get
        res_get = await client.get(f"/api/v1/spatial-proteogenomics/studies/{study_id}", headers=auth_headers)
        assert res_get.status_code == 200
        assert res_get.json()["tissue_sample_id"] == "GBM_TME_Slice_04"

        # Delete
        res_del = await client.delete(f"/api/v1/spatial-proteogenomics/studies/{study_id}", headers=auth_headers)
        assert res_del.status_code == 204
