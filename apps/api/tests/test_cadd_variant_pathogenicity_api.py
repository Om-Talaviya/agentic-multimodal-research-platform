"""Tests for CADD Variant Pathogenicity API."""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_cadd_variant_api_endpoints(auth_headers: dict) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "study_name": "API CADD Test Study",
            "genome_build": "GRCh38",
            "target_gene": "TP53",
            "variants": [
                {
                    "chromosome": "chr17",
                    "position": 7674220,
                    "reference_allele": "C",
                    "alternate_allele": "T",
                    "hgvs_c": "c.743G>A",
                }
            ],
        }
        res = await client.post("/api/v1/cadd-variant-pathogenicity/score-variants", json=payload, headers=auth_headers)
        assert res.status_code == 201, res.text
        data = res.json()
        assert data["study_name"] == "API CADD Test Study"
        study_id = data["id"]
        assert len(data["variants"]) == 1

        # List
        res_list = await client.get("/api/v1/cadd-variant-pathogenicity/studies", headers=auth_headers)
        assert res_list.status_code == 200
        assert any(s["id"] == study_id for s in res_list.json())

        # Get
        res_get = await client.get(f"/api/v1/cadd-variant-pathogenicity/studies/{study_id}", headers=auth_headers)
        assert res_get.status_code == 200
        assert res_get.json()["target_gene"] == "TP53"

        # Delete
        res_del = await client.delete(f"/api/v1/cadd-variant-pathogenicity/studies/{study_id}", headers=auth_headers)
        assert res_del.status_code == 204
