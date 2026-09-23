import pytest
from database.repositories.car_macrophage_repo import CARMacrophageRepository


@pytest.mark.asyncio
async def test_car_macrophage_repo_lifecycle(db_session):
    repo = CARMacrophageRepository(db_session)

    design = await repo.create_design(
        construct_name="Anti-Mesothelin CAR-M (Megf10/FcR)",
        target_tumor_antigen="Mesothelin (MSLN)",
        scfv_domain="Amatuximab-derived SS1",
        intracellular_signaling_domain="Megf10 + FcR-gamma",
        macrophage_subtype="M1 Pro-Inflammatory",
        matrix_degradation_mmp_score=8.9,
        target_phagocytosis_efficiency_percent=82.0,
    )

    assert design.id is not None
    assert design.construct_name == "Anti-Mesothelin CAR-M (Megf10/FcR)"

    record = await repo.add_phagocytosis_record(
        design_id=design.id,
        target_cell_line="OVCAR-3 Ovarian Carcinoma",
        effector_to_target_ratio="3:1",
        trogocytosis_rate_percent=14.2,
        whole_cell_engulfment_rate_percent=71.5,
        antigen_cross_presentation_index=0.92,
    )
    assert record.target_cell_line == "OVCAR-3 Ovarian Carcinoma"

    tme = await repo.add_tme_profile(
        design_id=design.id,
        tnf_alpha_secretion_pg_ml=1450.0,
        il12_secretion_pg_ml=890.0,
        il10_immunosuppression_fold_reduction=4.2,
        collagen_matrix_clearance_percent=68.4,
    )
    assert tme.collagen_matrix_clearance_percent == 68.4

    retrieved = await repo.get_design(design.id)
    assert retrieved is not None
    assert len(retrieved.phagocytosis_records) == 1
    assert len(retrieved.tme_profiles) == 1
