"""Tests for Metagenomic AMR Surveillance Engine."""
import pytest
from research.amr.amr_engine import MetagenomicAMREngine


def test_amr_engine_analysis_default():
    engine = MetagenomicAMREngine()
    result = engine.analyze_sample({
        "sample_name": "Municipal Wastewater Plant Run",
        "sample_type": "WASTEWATER",
        "collection_location": "North Basin",
        "total_reads_sequenced": 15000000,
    })

    assert result["sample_name"] == "Municipal Wastewater Plant Run"
    assert result["sample_type"] == "WASTEWATER"
    assert len(result["pathogens"]) == 4
    assert len(result["amr_genes"]) == 5
    assert result["outbreak_risk_level"] in ["LOW", "ELEVATED", "CRITICAL"]


def test_amr_engine_custom_pathogens_and_amr():
    engine = MetagenomicAMREngine()
    custom_pathogens = [
        {
            "taxon_name": "Mycobacterium tuberculosis",
            "ncbi_taxid": 1773,
            "relative_abundance_pct": 5.0,
            "read_depth": 50000,
            "pathogenicity_grade": "HIGH_CONSEQUENCE",
            "is_priority_pathogen": True,
        }
    ]
    custom_amr = [
        {
            "gene_symbol": "rpoB_S450L",
            "resistance_mechanism": "RNA_POLYMERASE_MUTATION",
            "drug_class": "RIFAMYCINS",
            "identity_pct": 100.0,
            "coverage_pct": 100.0,
            "plasmid_mediated": False,
        }
    ]

    result = engine.analyze_sample(
        sample_input={"sample_name": "Sputum Metagenome", "sample_type": "CLINICAL_ISOLATE"},
        raw_pathogens=custom_pathogens,
        raw_amr_genes=custom_amr,
    )

    assert result["sample_name"] == "Sputum Metagenome"
    assert len(result["pathogens"]) == 1
    assert result["pathogens"][0]["taxon_name"] == "Mycobacterium tuberculosis"
    assert len(result["amr_genes"]) == 1
    assert result["amr_genes"][0]["gene_symbol"] == "rpoB_S450L"
