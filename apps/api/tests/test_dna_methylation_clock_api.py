"""Tests for DNA Methylation Clock API."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_dna_methylation_clock_api_endpoints(auth_headers: dict) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "study_name": "API Methylation Test",
            "sample_identifier": "DONOR-API-01",
            "tissue_type": "whole_blood",
            "chronological_age": 42.0,
            "cpg_probes": [
                {
                    "cpg_probe_id": "cg02228185",
                    "target_gene": "ASPA",
                    "chromosome": "chr17",
                    "genomic_coordinate": 3387820,
                    "beta_value": 0.45,
                    "clock_weight": 1.45,
                }
            ],
        }
        res = await client.post("/api/v1/dna-methylation-clock/estimate-age", json=payload, headers=auth_headers)
        assert res.status_code == 201, res.text
        data = res.json()
        assert data["study_name"] == "API Methylation Test"
        study_id = data["id"]
        assert len(data["cpg_markers"]) == 1

        # List
        res_list = await client.get("/api/v1/dna-methylation-clock/studies", headers=auth_headers)
        assert res_list.status_code == 200
        assert any(s["id"] == study_id for s in res_list.json())

        # Get
        res_get = await client.get(f"/api/v1/dna-methylation-clock/studies/{study_id}", headers=auth_headers)
        assert res_get.status_code == 200
        assert res_get.json()["sample_identifier"] == "DONOR-API-01"

        # Delete
        res_del = await client.delete(f"/api/v1/dna-methylation-clock/studies/{study_id}", headers=auth_headers)
        assert res_del.status_code == 204
