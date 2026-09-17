import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_cancer_vaccine_api_endpoints(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Design Vaccine
        payload = {
            "patient_id": "PT-TEST-API-99",
            "tumor_type": "Cutaneous Melanoma",
            "hla_alleles": ["HLA-A*02:01", "HLA-A*24:02"],
            "mutations": [
                {
                    "mutated_gene": "BRAF (V600E)",
                    "mutation_type": "SNV",
                    "peptide_mt": "EDLTVKIGDF",
                    "peptide_wt": "EDLTVKIGFL",
                    "hla_allele": "HLA-A*02:01",
                    "vaf_pct": 48.2,
                    "expression_tpm": 310.5
                },
                {
                    "mutated_gene": "KRAS (G12D)",
                    "mutation_type": "SNV",
                    "peptide_mt": "KLVVVGADGV",
                    "peptide_wt": "KLVVVGAGGV",
                    "hla_allele": "HLA-A*02:01",
                    "vaf_pct": 36.1,
                    "expression_tpm": 125.0
                }
            ],
            "polyepitope_linker": "AAY",
            "adjuvant_type": "Poly-ICLC"
        }
        res = await client.post("/api/v1/cancer-vaccines/design", json=payload, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert "vaccine_id" in data
        vaccine_id = data["vaccine_id"]

        # 2. List Designs
        res_list = await client.get("/api/v1/cancer-vaccines/designs", headers=auth_headers)
        assert res_list.status_code == 200
        designs = res_list.json()
        assert len(designs) >= 1

        # 3. Get Single Design
        res_get = await client.get(f"/api/v1/cancer-vaccines/designs/{vaccine_id}", headers=auth_headers)
        assert res_get.status_code == 200
        detail = res_get.json()
        assert detail["id"] == vaccine_id
        assert len(detail["neoepitopes"]) == 2
        assert len(detail["schedules"]) == 1
