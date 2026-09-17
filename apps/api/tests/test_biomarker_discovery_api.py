"""Tests for Multi-Modal Biomarker Discovery API endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_biomarker_discovery_api_endpoints(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Extract signature
        payload = {
            "study_title": "Anti-PD1 Immunotherapy Signature Study",
            "disease_indication": "Melanoma",
            "cohort_sample_size": 140,
            "omics_layers": ["TRANSCRIPTOMICS", "PROTEOMICS", "METABOLOMICS"],
        }
        res = await client.post("/api/v1/biomarkers/studies/extract", json=payload, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert "id" in data
        assert data["study_title"] == "Anti-PD1 Immunotherapy Signature Study"
        assert len(data["features"]) >= 4
        assert len(data["stratifications"]) == 3
        study_id = data["id"]

        # 2. List Studies
        res_list = await client.get("/api/v1/biomarkers/studies", headers=auth_headers)
        assert res_list.status_code == 200
        studies = res_list.json()
        assert len(studies) >= 1

        # 3. Get Study Details
        res_get = await client.get(f"/api/v1/biomarkers/studies/{study_id}", headers=auth_headers)
        assert res_get.status_code == 200
        details = res_get.json()
        assert details["id"] == study_id
        assert details["disease_indication"] == "Melanoma"
        assert len(details["features"]) >= 4
