"""Tests for Metagenomic Pathogen Surveillance & AMR API endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.src.api.main import app


@pytest.mark.asyncio
async def test_amr_surveillance_api_endpoints(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Analyze sample
        payload = {
            "sample_name": "Municipal Outfall Monitoring",
            "sample_type": "WASTEWATER",
            "collection_location": "Bayside Water Works",
            "total_reads_sequenced": 8000000,
        }
        res = await client.post("/api/v1/amr/samples/analyze", json=payload, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert "id" in data
        assert data["sample_name"] == "Municipal Outfall Monitoring"
        assert len(data["pathogens"]) == 4
        assert len(data["amr_genes"]) == 5
        sample_id = data["id"]

        # 2. List Samples
        res_list = await client.get("/api/v1/amr/samples", headers=auth_headers)
        assert res_list.status_code == 200
        samples = res_list.json()
        assert len(samples) >= 1

        # 3. Get Sample Details
        res_get = await client.get(f"/api/v1/amr/samples/{sample_id}", headers=auth_headers)
        assert res_get.status_code == 200
        details = res_get.json()
        assert details["id"] == sample_id
        assert details["collection_location"] == "Bayside Water Works"
        assert len(details["pathogens"]) == 4
        assert len(details["amr_genes"]) == 5
