"""Tests for Phase 524: Autonomous Picoliter Microfluidic Droplet Single-Cell Mass Spectrometry Proteome Fingerprinter."""

import pytest
from research.orchestration.droplet_single_cell_mass_spec_proteomics_engine import DropletSingleCellMassSpecProteomicsEngine


def test_droplet_single_cell_mass_spec_proteomics_engine():
    engine = DropletSingleCellMassSpecProteomicsEngine()
    result = engine.analyze(
        target_specimen="Direct Microfluidic Nano-Electrospray Ionization (nanoESI) Orbitrap MS of Individual Single Glioblastoma Cells",
        analytical_modality="droplet-single-cell-proteomics",
        input_scale=1.0,
    )

    assert result.target_specimen == "Direct Microfluidic Nano-Electrospray Ionization (nanoESI) Orbitrap MS of Individual Single Glioblastoma Cells"
    assert result.confidence_score >= 0.95
    assert result.quantified_proteins_per_single_cell_count != 0.0
    assert result.median_protein_sequence_coverage_pct != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Picoliter Microflui" in result.summary_report
