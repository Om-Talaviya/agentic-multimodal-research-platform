"""API integration tests for HLA LOH & Immune Evasion Engine (Phase 135)."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_hla_loh_resistance_api_workflow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Evaluate HLA LOH
        payload = {
            "patient_id": "PT_LUNG_772",
            "tumor_type": "Lung Adenocarcinoma",
            "tumor_purity": 0.72,
            "alleles": [
                {"hla_gene": "HLA-A", "allele_name": "HLA-A*02:01", "baf_tumor": 0.05, "purity": 0.72},
                {"hla_gene": "HLA-A", "allele_name": "HLA-A*11:01", "baf_tumor": 0.95, "purity": 0.72},
                {"hla_gene": "HLA-B", "allele_name": "HLA-B*08:01", "baf_tumor": 0.49, "purity": 0.72},
                {"hla_gene": "HLA-B", "allele_name": "HLA-B*15:01", "baf_tumor": 0.51, "purity": 0.72},
            ],
        }
        res_post = await client.post("/api/v1/hla-loh/evaluate", json=payload, headers=auth_headers)
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "study_id" in data_post
        assert data_post["patient_id"] == "PT_LUNG_772"
        assert data_post["loh_alleles_count"] == 1
        study_id = data_post["study_id"]

        # 2. Retrieve study details
        res_get = await client.get(f"/api/v1/hla-loh/studies/{study_id}", headers=auth_headers)
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == study_id
        assert data_get["patient_cohort_id"] == "PT_LUNG_772"
        assert data_get["allele_profiles_count"] == 4
        assert data_get["evasion_scores_count"] == 1
