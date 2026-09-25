"""Tests for TCR/BCR Clonotype Tracking API."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_tcr_clonotype_api_endpoints(auth_headers: dict) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "study_name": "API Repertoire Study",
            "sample_source": "TIL",
            "repertoire_type": "TCR_alpha_beta",
            "clonotypes": [
                {
                    "cdr3_amino_acid": "CASSIRSSYEQYF",
                    "v_gene": "TRBV19",
                    "j_gene": "TRBJ2-7",
                    "clone_frequency": 0.22,
                    "antigen_specificity": "Tumor_Antigen",
                }
            ],
        }
        res = await client.post("/api/v1/tcr-clonotype-tracking/analyze", json=payload, headers=auth_headers)
        assert res.status_code == 201, res.text
        data = res.json()
        assert data["study_name"] == "API Repertoire Study"
        study_id = data["id"]
        assert len(data["clonotypes"]) == 1

        # List
        res_list = await client.get("/api/v1/tcr-clonotype-tracking/studies", headers=auth_headers)
        assert res_list.status_code == 200
        assert any(s["id"] == study_id for s in res_list.json())

        # Get
        res_get = await client.get(f"/api/v1/tcr-clonotype-tracking/studies/{study_id}", headers=auth_headers)
        assert res_get.status_code == 200
        assert res_get.json()["sample_source"] == "TIL"

        # Delete
        res_del = await client.delete(f"/api/v1/tcr-clonotype-tracking/studies/{study_id}", headers=auth_headers)
        assert res_del.status_code == 204
