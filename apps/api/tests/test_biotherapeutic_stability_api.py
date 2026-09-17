import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_biotherapeutic_stability_api_endpoints(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Analyze Stability
        payload = {
            "construct_name": "Test-mAb-Lead-09",
            "modality": "mAb",
            "heavy_chain_sequence": "EVQLVESGGGLVQPGGSLRLSCAASGFNIKDTYIHWVRQAPGKGLEWVARIYPTNGYTRYADSVKGRFTISADTSKNTAYLQMNSLRAEDTAVYYCSRWGGDGFYAMDYWGQGTLVTVSSASTKGPSVFPLAPSSKSTSGGTAALGCLVKDYFPEPVTVSWNSGALTSGVHTFPAVLQSSGLYSLSSVVTVPSSSLGTQTYICNVNHKPSNTKVDKKVEPKSC",
            "light_chain_sequence": "DIQMTQSPSSLSASVGDRVTITCRASQDVNTAVAWYQQKPGKAPKLLIYSASFLYSGVPSRFSGSRSGTDFTLTISSLQPEDFATYYCQQHYTTPPTFGQGTKVEIKRTVAAPSVFIFPPSDEQLKSGTASVVCLLNNFYPREAKVQWKVDNALQSGNSQESVTEQDSKDSTYSLSSTLTLSKADYEKHKVYACEVTHQGLSSPVTKSFNRGEC",
            "buffer_type": "Histidine",
            "ph": 6.0,
            "surfactant": "Polysorbate 80",
            "tonicity_agent": "Sucrose"
        }
        res = await client.post("/api/v1/biotherapeutic-stability/analyze", json=payload, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert "construct_id" in data
        assert data["monomer_retention_pct_at_40c"] >= 90.0
        cid = data["construct_id"]

        # 2. List Constructs
        res_list = await client.get("/api/v1/biotherapeutic-stability/constructs", headers=auth_headers)
        assert res_list.status_code == 200
        constructs = res_list.json()
        assert len(constructs) >= 1

        # 3. Get Single Construct
        res_get = await client.get(f"/api/v1/biotherapeutic-stability/constructs/{cid}", headers=auth_headers)
        assert res_get.status_code == 200
        detail = res_get.json()
        assert detail["id"] == cid
        assert len(detail["excipient_screens"]) == 1
