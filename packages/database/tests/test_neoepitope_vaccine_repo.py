import pytest
import pytest_asyncio
from database.models.neoepitope_vaccine import DBCancerVaccineDesign
from database.repositories.neoepitope_vaccine_repo import NeoepitopeVaccineRepository

@pytest.mark.asyncio
async def test_neoepitope_vaccine_repository(async_db_session):
    repo = NeoepitopeVaccineRepository(async_db_session)

    # 1. Create vaccine design
    vaccine = await repo.create_vaccine_design(
        patient_id="PT-TEST-001",
        tumor_type="Melanoma",
        hla_alleles=["HLA-A*02:01", "HLA-A*24:02"],
        mrna_construct_sequence="MKWVTFISLLFLFSSAYS_KLVVVGADGVAAYFLTETLTVVL_MITD",
        polyepitope_junction_cleavability_score=0.91,
        predicted_immunogenicity_index=0.94,
    )
    assert vaccine.id is not None
    assert vaccine.patient_id == "PT-TEST-001"

    # 2. Add candidate neoepitope
    epitope = await repo.add_candidate_neoepitope(
        vaccine_id=vaccine.id,
        mutated_gene="KRAS",
        mutation_type="SNV",
        peptide_sequence="KLVVVGADGV",
        wildtype_sequence="KLVVVGAGGV",
        hla_restriction="HLA-A*02:01",
        mhc_binding_affinity_ic50_nm=24.5,
        clonality_vaf_pct=42.0,
        expression_tpm=150.0,
        immunogenicity_rank_score=0.95,
        is_selected_for_vaccine=True,
    )
    assert epitope.id is not None
    assert epitope.vaccine_id == vaccine.id

    # 3. Add adjuvant schedule
    schedule = await repo.add_adjuvant_schedule(
        vaccine_id=vaccine.id,
        adjuvant_type="Poly-ICLC",
        dose_schedule_days=[0, 3, 7, 14, 28, 56],
        booster_frequency_weeks=4,
        predicted_cd8_tcell_response_pct=78.2,
    )
    assert schedule.id is not None

    # 4. Fetch hydrated vaccine
    fetched = await repo.get_vaccine_design_by_id(vaccine.id)
    assert fetched is not None
    assert len(fetched.neoepitopes) == 1
    assert len(fetched.schedules) == 1
    assert fetched.neoepitopes[0].mutated_gene == "KRAS"
