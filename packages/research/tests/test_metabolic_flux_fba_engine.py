"""Tests for Metabolic Flux FBA Engine."""

import pytest
from research.metabolism.metabolic_flux_fba_engine import MetabolicFluxFBAEngine


def test_metabolic_flux_fba_engine_simulation() -> None:
    engine = MetabolicFluxFBAEngine()
    result = engine.run_flux_balance_analysis(
        study_name="Warburg Glycolysis FBA Study",
        organism_model="Human Recon3D",
        cellular_phenotype="Warburg Glycolytic Cancer",
    )

    assert result["study_name"] == "Warburg Glycolysis FBA Study"
    assert result["optimal_growth_rate_hr"] > 0.05
    assert len(result["reactions"]) == 4
    assert len(result["vulnerabilities"]) >= 3

    # Check reaction properties
    first_rxn = result["reactions"][0]
    assert "reaction_id" in first_rxn
    assert "computed_flux_mmol_gdw_hr" in first_rxn
    assert "shadow_price" in first_rxn

    # Check vulnerability properties
    first_vuln = result["vulnerabilities"][0]
    assert "target_enzyme_gene" in first_vuln
    assert "growth_inhibition_percent" in first_vuln
