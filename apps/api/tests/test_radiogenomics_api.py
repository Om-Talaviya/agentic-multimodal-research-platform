"""API integration tests for Radiogenomics & 3D Imaging AI endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_radiogenomics_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Extract and Correlate
        payload = {
            "patient_id": "TCGA-GBM-9912",
            "modality": "MRI_T1_CONTRAST",
            "anatomical_region": "BRAIN_GLIOMA",
            "lesion_volume_cm3": 35.0,
        }
        res_ex = await client.post("/api/v1/radiogenomics/extract", json=payload, headers=auth_headers)
        assert res_ex.status_code == 201
        data_ex = res_ex.json()
        assert data_ex["status"] == "success"
        assert "id" in data_ex
        scan_id = data_ex["id"]
        assert data_ex["radiomic_features_count"] >= 7
        assert data_ex["genomic_correlations_count"] >= 1

        # 2. List Scans
        res_list = await client.get("/api/v1/radiogenomics/scans", headers=auth_headers)
        assert res_list.status_code == 200
        list_data = res_list.json()
        assert len(list_data) >= 1
        assert any(s["id"] == scan_id for s in list_data)

        # 3. Get Scan Details
        res_get = await client.get(f"/api/v1/radiogenomics/scans/{scan_id}", headers=auth_headers)
        assert res_get.status_code == 200
        get_data = res_get.json()
        assert get_data["id"] == scan_id
        assert get_data["patient_id"] == "TCGA-GBM-9912"
        assert len(get_data["radiomic_features"]) >= 7
        assert len(get_data["genomic_correlations"]) >= 1
