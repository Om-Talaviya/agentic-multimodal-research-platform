"""Tests for siRNA Thermodynamics Repository."""

import pytest
from database.connection import AsyncSession
from database.repositories.sirna_thermodynamics_repo import SiRNAThermodynamicsRepository


@pytest.mark.asyncio
async def test_sirna_thermodynamics_repo_crud(db_session: AsyncSession) -> None:
    repo = SiRNAThermodynamicsRepository(db_session)

    study = await repo.create_study(
        study_name="Test siRNA Silencing Study",
        target_mrna_transcript="NM_000546.6 (TP53)",
        target_gene="TP53",
        candidates_screened=1,
        best_candidate_guide_strand="5'-UUGAGGAACUGUGAAUUUGAG-3'",
        mean_on_target_efficiency=92.5,
        summary_metrics={"score": 92.5},
        duplexes=[
            {
                "guide_strand_sequence": "5'-UUGAGGAACUGUGAAUUUGAG-3'",
                "passenger_strand_sequence": "5'-CAAAUUCACAGUUCCUCAAUU-3'",
                "delta_g_5p_kcal_mol": -6.8,
                "delta_g_3p_kcal_mol": -9.4,
                "delta_delta_g_asymmetry": 2.6,
                "seed_region_tm_celsius": 48.2,
                "risc_loading_preference": "guide_dominant",
                "predicted_knockdown_efficiency": 93.7,
                "chemical_mod_pattern": "2OMe_2F_phosphorothioate",
            }
        ],
        off_targets=[
            {
                "off_target_gene": "MDM2",
                "utr3_seed_match_type": "7mer-m8",
                "seed_binding_free_energy": -5.2,
                "off_target_silencing_risk": "low",
            }
        ],
    )

    assert study.id is not None
    assert study.study_name == "Test siRNA Silencing Study"
    assert len(study.duplexes) == 1
    assert len(study.off_targets) == 1

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.target_gene == "TP53"

    studies = await repo.list_studies()
    assert len(studies) >= 1

    deleted = await repo.delete_study(study.id)
    assert deleted is True

    empty = await repo.get_study(study.id)
    assert empty is None
