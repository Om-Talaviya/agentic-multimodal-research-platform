"""Tests for Liquid Biopsy API endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_liquid_biopsy_api_endpoints(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Analyze Sample
        payload = {
            "patient_id": "PT-CRC-882",
            "sample_barcode": "LB-2026-0941",
            "cancer_type": "Colorectal Adenocarcinoma",
            "sampling_timepoint": "POST_SURGERY",
            "total_cfdna_ng_ml": 14.8,
            "short_fragments_100_150bp": 42000,
            "long_fragments_160_220bp": 98000
        }
        res = await client.post("/api/v1/liquid-biopsy/samples/analyze", json=payload, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert "id" in data
        assert data["patient_id"] == "PT-CRC-882"
        assert data["mrd_status"] in ["MRD_POSITIVE", "MRD_NEGATIVE", "INDETERMINATE"]
        assert len(data["size_distributions"]) >= 1
        assert len(data["end_motifs"]) >= 1
        sample_id = data["id"]

        # 2. List Samples
        res_list = await client.get("/api/v1/liquid-biopsy/samples", headers=auth_headers)
        assert res_list.status_code == 200
        samples = res_list.json()
        assert len(samples) >= 1

        # 3. Get Sample Details
        res_get = await client.get(f"/api/v1/liquid-biopsy/samples/{sample_id}", headers=auth_headers)
        assert res_get.status_code == 200
        details = res_get.json()
        assert details["id"] == sample_id
        assert details["sample_barcode"] == "LB-2026-0941"
        assert len(details["size_distributions"]) >= 1
        assert len(details["end_motifs"]) >= 1
