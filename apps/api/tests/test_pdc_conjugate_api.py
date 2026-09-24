"""
API integration tests for Phase 165: PDC Conjugate.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from main import app


@pytest.mark.asyncio
async def test_pdc_conjugate_api_flow(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Evaluate PDC
        payload = {
            "pdc_name": "cRGD-ValCit-MMAE_Test",
            "homing_peptide_sequence": "cyclo(RGDfK)",
            "linker_type": "Val-Cit-PABC",
            "cytotoxic_payload": "Monomethyl Auristatin E (MMAE)",
        }
        res_post = await client.post(
            "/api/v1/pdc-conjugate/evaluate",
            json=payload,
            headers=auth_headers,
        )
        assert res_post.status_code == 201
        data_post = res_post.json()
        assert data_post["status"] == "SUCCESS"
        assert "study_id" in data_post
        study_id = data_post["study_id"]
        assert data_post["pdc_name"] == "cRGD-ValCit-MMAE_Test"
        assert data_post["plasma_stability_half_life_hours"] > 0

        # 2. Get study
        res_get = await client.get(
            f"/api/v1/pdc-conjugate/studies/{study_id}",
            headers=auth_headers,
        )
        assert res_get.status_code == 200
        data_get = res_get.json()
        assert data_get["id"] == study_id
        assert data_get["pdc_name"] == "cRGD-ValCit-MMAE_Test"
        assert "cleavage_profiles_count" in data_get
