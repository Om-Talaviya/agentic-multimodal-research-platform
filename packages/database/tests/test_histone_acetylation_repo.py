import pytest
from database.repositories.histone_acetylation_repo import HistoneAcetylationRepository


@pytest.mark.asyncio
async def test_histone_acetylation_repo_lifecycle(db_session):
    repo = HistoneAcetylationRepository(db_session)

    model = await repo.create_model(
        locus_name="MYC Super-Enhancer Locus",
        genomic_coordinates="chr8:127735434-127736300",
        cell_line_or_tissue="K562 Chronic Myelogenous Leukemia",
        initial_h3k27ac_enrichment=14.8,
        hdac_inhibitor_name="Romidepsin (FK228)",
        predicted_enhancer_activation_fold=5.6,
    )

    assert model.id is not None
    assert model.locus_name == "MYC Super-Enhancer Locus"

    kinetics = await repo.add_enzyme_kinetics(
        model_id=model.id,
        enzyme_type="HDAC1/2",
        catalytic_rate_kcat=12.5,
        michaelis_constant_km_um=45.0,
        inhibition_constant_ki_nm=3.2,
    )
    assert kinetics.enzyme_type == "HDAC1/2"

    profile = await repo.add_chromatin_profile(
        model_id=model.id,
        time_point_hours=6.0,
        nucleosome_occupancy_percent=24.5,
        atac_seq_peak_intensity_rpm=88.4,
        brd4_bromodomain_recruitment=7.8,
    )
    assert profile.atac_seq_peak_intensity_rpm == 88.4

    retrieved = await repo.get_model(model.id)
    assert retrieved is not None
    assert len(retrieved.enzyme_kinetics) == 1
    assert len(retrieved.chromatin_profiles) == 1
