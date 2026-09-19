"""API integration tests for Proteogenomics & Mass Spectrometry Spectral Libraries (Phase 95)."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_proteogenomics_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Generate theoretical fragmentation spectrum
        res_spec = await client.post(
            "/api/v1/proteogenomics/fragmentation-spectrum",
            json={"peptide_sequence": "LVNEVTEFAK", "charge": 2},
            headers=auth_headers,
        )
        assert res_spec.status_code == 200
        data_spec = res_spec.json()
        assert data_spec["status"] == "SUCCESS"
        assert "spectrum" in data_spec
        assert len(data_spec["spectrum"]["b_ions"]) > 0
        assert len(data_spec["spectrum"]["y_ions"]) > 0

        # 2. Run proteogenomic search
        search_payload = {
            "sample_id": "Melanoma_Patient_Tumor_MS01",
            "instrument_type": "Orbitrap Exploris 480",
            "search_database": "UniProtKB + Ribo-Seq Novel ORFs",
            "fdr_threshold": 0.01,
        }
        res_post = await client.post("/api/v1/proteogenomics/search", json=search_payload, headers=auth_headers)
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "experiment_id" in data_post
        assert data_post["identified_peptides_count"] > 0
        exp_id = data_post["experiment_id"]

        # 3. Retrieve experiment details
        res_get = await client.get(f"/api/v1/proteogenomics/experiments/{exp_id}", headers=auth_headers)
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == exp_id
        assert data_get["sample_id"] == "Melanoma_Patient_Tumor_MS01"
        assert len(data_get["psm_matches"]) > 0
        assert len(data_get["novel_junctions"]) > 0
