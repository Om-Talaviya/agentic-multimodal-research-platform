"""Tests for Cryo-ET Subtomogram Engine."""
import pytest
from research.cryoet.subtomogram_engine import CryoETSubtomogramEngine


def test_reconstruct_and_average_default():
    engine = CryoETSubtomogramEngine()
    dataset_input = {
        "sample_name": "In-Situ Ribosome",
        "specimen_organism": "S. cerevisiae",
        "cellular_compartment": "CYTOSOL",
        "tilt_angle_min": -60.0,
        "tilt_angle_max": 60.0,
        "pixel_size_angstrom": 1.35,
        "total_tilt_images": 41,
    }

    result = engine.reconstruct_and_average(dataset_input)
    assert result["sample_name"] == "In-Situ Ribosome"
    assert len(result["particles"]) >= 10
    assert "refinement" in result
    assert result["refinement"]["estimated_resolution_angstrom"] > 0
    assert len(result["refinement"]["fsc_curve_json"]) >= 5
    assert result["dataset_metadata_json"]["missing_wedge_angle_deg"] == 60.0


def test_reconstruct_and_average_custom_particles():
    engine = CryoETSubtomogramEngine()
    dataset_input = {
        "sample_name": "ATP Synthase",
        "pixel_size_angstrom": 1.5,
    }
    particles = [
        {"particle_index": 1, "coord_x": 100, "coord_y": 200, "coord_z": 50, "class_assignment": "CLASS_1"},
        {"particle_index": 2, "coord_x": 150, "coord_y": 250, "coord_z": 60, "class_assignment": "CLASS_1"},
    ]

    result = engine.reconstruct_and_average(dataset_input, particles)
    assert len(result["particles"]) == 2
    assert result["refinement"]["particles_averaged_count"] == 2
