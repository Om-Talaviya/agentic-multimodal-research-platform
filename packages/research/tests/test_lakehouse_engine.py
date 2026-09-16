"""Unit tests for ScientificLakehouseEngine (Phase 52)."""
import pytest
from research.lakehouse.lakehouse_engine import ScientificLakehouseEngine


def test_lakehouse_engine_schema_validation():
    engine = ScientificLakehouseEngine()

    # Valid schema validation
    schema = engine.validate_schema(
        modality="GENOMIC",
        storage_format="PARQUET",
        schema_def={"partition_keys": ["study_id"]}
    )
    assert schema["modality"] == "GENOMIC"
    assert schema["format"] == "PARQUET"
    assert len(schema["columns"]) >= 4

    # Invalid modality error handling
    with pytest.raises(ValueError):
        engine.validate_schema(modality="INVALID_MODALITY", storage_format="PARQUET", schema_def={})

    # Incompatible format for modality error handling
    with pytest.raises(ValueError):
        engine.validate_schema(modality="IMAGING", storage_format="FASTA", schema_def={})


def test_lakehouse_engine_hybrid_query_execution():
    engine = ScientificLakehouseEngine()

    result = engine.execute_hybrid_query(
        query_text="Identify kinase inhibitor resistance mutations in EGFR",
        target_tables=["pan_cancer_tcga_rnaseq", "alphafold_kinase_pdb"],
        sql_predicate="fold_change > 2.0",
        vector_threshold=0.80,
        limit=5,
    )

    assert result["matched_records_count"] > 0
    assert result["execution_time_ms"] > 0
    assert len(result["results_preview"]) == result["matched_records_count"]
    for record in result["results_preview"]:
        assert record["vector_similarity"] >= 0.80
        assert "citation_uri" in record
        assert "entity_attributes" in record
