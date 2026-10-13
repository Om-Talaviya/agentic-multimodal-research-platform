"""Tests for Phase 449: Autonomous Microfluidic Droplet Single-Cell Metabolic Metabolomics Isotope Labeling Profiler."""

import pytest
from research.orchestration.droplet_single_cell_isotope_metabolomics_engine import DropletSingleCellIsotopeMetabolomicsEngine


def test_droplet_single_cell_isotope_metabolomics_engine():
    engine = DropletSingleCellIsotopeMetabolomicsEngine()
    result = engine.analyze(
        target_specimen="Glucose-13C6 Labeled Glioblastoma Stem-Like Cells in Monodisperse Fluorocarbon Droplets",
        analytical_modality="single-cell-droplet-metabolomics",
        input_scale=1.0,
    )

    assert result.target_specimen == "Glucose-13C6 Labeled Glioblastoma Stem-Like Cells in Monodisperse Fluorocarbon Droplets"
    assert result.confidence_score >= 0.95
    assert result.isotopic_enrichment_m3_lactate_ratio != 0.0
    assert result.droplet_generation_frequency_khz != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Microfluidic Drople" in result.summary_report
