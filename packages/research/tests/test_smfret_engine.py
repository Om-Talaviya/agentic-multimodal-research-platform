"""Tests for Single-Molecule FRET Kinetics engine."""
import pytest
from research.smfret.smfret_engine import SmFRETKineticsEngine


def test_smfret_kinetics_analysis_default():
    engine = SmFRETKineticsEngine()
    result = engine.analyze_experiment({
        "experiment_title": "T4 Lysozyme Hinge Motion",
        "macromolecule_name": "T4 Lysozyme",
        "donor_fluorophore": "Cy3",
        "acceptor_fluorophore": "Cy5",
        "forster_radius_angstrom": 54.0,
        "acquisition_rate_hz": 100.0,
    })

    assert result["experiment_title"] == "T4 Lysozyme Hinge Motion"
    assert result["macromolecule_name"] == "T4 Lysozyme"
    assert result["state_count"] == 3
    assert len(result["states"]) == 3
    assert len(result["traces"]) >= 1

    first_trace = result["traces"][0]
    assert "trace_data_json" in first_trace
    assert len(first_trace["trace_data_json"]) == 200
    assert "distance_angstrom" in first_trace["trace_data_json"][0]


def test_smfret_custom_traces():
    engine = SmFRETKineticsEngine()
    custom_trace = [
        {
            "molecule_index": 99,
            "total_frames": 10,
            "mean_fret_efficiency": 0.55,
            "photobleaching_frame": 10,
            "trace_data_json": [{"frame": i, "fret_eff": 0.55} for i in range(10)],
        }
    ]
    result = engine.analyze_experiment(
        experiment_input={"macromolecule_name": "Ribosome A-site"},
        raw_traces_input=custom_trace,
    )

    assert result["macromolecule_name"] == "Ribosome A-site"
    assert result["total_molecules_recorded"] == 1
    assert result["traces"][0]["molecule_index"] == 99
