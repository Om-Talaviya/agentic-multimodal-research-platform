"""Tests for Metabolic Flux FBA Repository."""

import pytest
from database.connection import AsyncSession
from database.repositories.metabolic_flux_fba_repo import MetabolicFluxFBARepository


@pytest.mark.asyncio
async def test_metabolic_flux_fba_repo_crud(db_session: AsyncSession) -> None:
    repo = MetabolicFluxFBARepository(db_session)

    study = await repo.create_study(
        study_name="Test Warburg FBA",
        organism_model="Human Recon3D",
        cellular_phenotype="Warburg Cancer",
        optimal_growth_rate_hr=0.084,
        objective_reaction="Biomass_Production",
        summary_metrics={"score": 0.084},
        reactions=[
            {
                "reaction_id": "R_HEX1",
                "reaction_name": "Hexokinase",
                "subsystem": "Glycolysis",
                "lower_bound": 0.0,
                "upper_bound": 1000.0,
                "computed_flux_mmol_gdw_hr": 14.85,
                "shadow_price": -0.12,
            }
        ],
        vulnerabilities=[
            {
                "target_enzyme_gene": "LDHA",
                "target_reaction": "R_LDH_L",
                "growth_inhibition_percent": 78.5,
                "synthetic_lethal_partner": "OXPHOS Complex I",
                "druggability_verdict": "druggable_selective",
            }
        ],
    )

    assert study.id is not None
    assert study.study_name == "Test Warburg FBA"
    assert len(study.reactions) == 1
    assert len(study.vulnerabilities) == 1

    fetched = await repo.get_study(study.id)
    assert fetched is not None
    assert fetched.organism_model == "Human Recon3D"

    studies = await repo.list_studies()
    assert len(studies) >= 1

    deleted = await repo.delete_study(study.id)
    assert deleted is True

    empty = await repo.get_study(study.id)
    assert empty is None
