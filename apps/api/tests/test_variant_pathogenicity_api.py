"""Tests for Genomic Variant Pathogenicity API endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_variant_pathogenicity_api_endpoints(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Classify Variant
        payload = {
            "gene_symbol": "BRCA1",
            "hgvs_c": "c.5266dupC",
            "hgvs_p": "p.Gln1756Profs*74",
            "chromosome": "chr17",
            "genomic_position": 43044295,
            "ref_allele": "C",
            "alt_allele": "CC",
            "transcript_id": "NM_007294.4",
            "consequence": "frameshift_variant",
            "allele_frequency_gnomad": 0.00001,
            "is_gene_lof_mechanism": True,
            "in_critical_domain": True,
            "alphamissense_score": 0.95,
            "cadd_phred": 32.0,
            "revel_score": 0.88,
            "clinvar_id": "VCV000017667"
        }
        res = await client.post("/api/v1/genomic-variants/classify", json=payload, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert "id" in data
        assert data["gene_symbol"] == "BRCA1"
        assert data["acmg_class"] in ["PATHOGENIC", "LIKELY_PATHOGENIC"]
        assert len(data["criteria"]) >= 1
        assert len(data["predictor_scores"]) == 4
        report_id = data["id"]

        # 2. List Reports
        res_list = await client.get("/api/v1/genomic-variants/reports", headers=auth_headers)
        assert res_list.status_code == 200
        reports = res_list.json()
        assert len(reports) >= 1

        # 3. Get Report Details
        res_get = await client.get(f"/api/v1/genomic-variants/reports/{report_id}", headers=auth_headers)
        assert res_get.status_code == 200
        details = res_get.json()
        assert details["id"] == report_id
        assert details["gene_symbol"] == "BRCA1"
        assert len(details["criteria"]) >= 1
        assert len(details["predictor_scores"]) == 4
