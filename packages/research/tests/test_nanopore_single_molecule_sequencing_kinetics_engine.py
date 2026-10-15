"""Tests for Phase 526: Autonomous Solid-State Nanopore Polymerase-Guided DNA Sequencing Kinetics Forecaster."""

import pytest
from research.orchestration.nanopore_single_molecule_sequencing_kinetics_engine import NanoporeSingleMoleculeSequencingKineticsEngine


def test_nanopore_single_molecule_sequencing_kinetics_engine():
    engine = NanoporeSingleMoleculeSequencingKineticsEngine()
    result = engine.analyze(
        target_specimen="Phi29 DNA Polymerase Coupled to Sub-2nm Si3N4 Solid-State Nanopore with Fluorescent dNTP Analogues",
        analytical_modality="nanopore-sequencing-kinetics",
        input_scale=1.0,
    )

    assert result.target_specimen == "Phi29 DNA Polymerase Coupled to Sub-2nm Si3N4 Solid-State Nanopore with Fluorescent dNTP Analogues"
    assert result.confidence_score >= 0.95
    assert result.nucleotide_incorporation_dwell_time_ms != 0.0
    assert result.polymerase_processivity_base_pairs != 0.0
    assert len(result.item_profiles) >= 3
    assert len(result.metric_traces) >= 3
    assert "Autonomous Solid-State Nanopor" in result.summary_report
