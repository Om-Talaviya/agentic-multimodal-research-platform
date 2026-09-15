"""Tests for SingleCellTranscriptomicsEngine."""

import pytest
from research.single_cell_engine import SingleCellTranscriptomicsEngine


def test_single_cell_engine_analysis_liver():
    engine = SingleCellTranscriptomicsEngine()

    result = engine.analyze_single_cell_dataset(
        dataset_title="Human Liver scRNA-seq LNP Uptake Atlas",
        organism="Homo sapiens",
        tissue="Liver",
        sequencing_platform="10x Chromium Next GEM 3' v3.1",
        clustering_resolution=0.5,
        total_cells_to_simulate=300,
    )

    assert result.dataset_title == "Human Liver scRNA-seq LNP Uptake Atlas"
    assert result.organism == "Homo sapiens"
    assert result.tissue == "Liver"
    assert len(result.clusters) == 6
    assert len(result.cell_coordinates) == 300
    assert len(result.differential_genes) > 0
    assert len(result.pathway_enrichments) > 0

    # Verify cluster properties
    c0 = result.clusters[0]
    assert c0.cell_type_annotation == "Mature Hepatocytes"
    assert c0.cell_count > 0
    assert len(c0.top_markers_json) > 0

    # Verify cell coordinate properties
    cell0 = result.cell_coordinates[0]
    assert cell0.cell_barcode.startswith("CELL_")
    assert -20.0 <= cell0.umap_x <= 20.0
    assert -20.0 <= cell0.umap_y <= 20.0
    assert 0.0 <= cell0.pseudotime_value <= 1.0

    # Verify differential genes
    diff0 = result.differential_genes[0]
    assert diff0.gene_symbol != ""
    assert diff0.log2_fold_change != 0.0
    assert 0.0 <= diff0.pct_in_cluster <= 1.0

    # Verify pathway enrichments
    path0 = result.pathway_enrichments[0]
    assert path0.normalized_enrichment_score > 0.0
    assert len(path0.leading_edge_genes_json) > 0
