import pytest
from database.repositories.hla_loh_resistance_repo import HLALOHResistanceRepository


@pytest.mark.asyncio
async def test_hla_loh_resistance_repo_lifecycle(db_session):
    repo = HLALOHResistanceRepository(db_session)

    study = await repo.create_study(
        patient_cohort_id="NSCLC_Cohort_PT88",
        tumor_type="Non-Small Cell Lung Cancer",
        total_alleles_analyzed=6,
        loh_positive_allele_count=2,
        overall_immune_evasion_index=0.78,
        checkpoint_resistance_prediction="High Resistance to Anti-PD1",
    )

    assert study.id is not None
    assert study.patient_cohort_id == "NSCLC_Cohort_PT88"

    allele = await repo.add_allele_profile(
        study_id=study.id,
        hla_gene="HLA-A",
        allele_identifier="HLA-A*02:01",
        tumor_copy_number=0.08,
        b_allele_frequency_baf=0.04,
        loh_status="DELETED",
    )
    assert allele.allele_identifier == "HLA-A*02:01"

    score = await repo.add_evasion_score(
        study_id=study.id,
        neoantigen_presentation_loss_percent=62.5,
        cd8_t_cell_evasion_probability=0.88,
        nk_cell_activation_potential=0.65,
        recommended_synthetic_rescue="NKG2A/KIR Blockade + Class II Peptides",
    )
    assert score.cd8_t_cell_evasion_probability == 0.88

    retrieved = await repo.get_study(study.id)
    assert retrieved is not None
    assert len(retrieved.allele_profiles) == 1
    assert len(retrieved.evasion_scores) == 1
