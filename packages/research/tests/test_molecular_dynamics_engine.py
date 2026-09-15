"""
Tests for MolecularDynamicsEngine.
"""

import pytest
from research.molecular_dynamics_engine import (
    MolecularDynamicsEngine,
    SimulationResult,
    TrajectoryFrameData,
    ResidueFluctuationData,
    QuantumPropertiesData,
)


def test_molecular_dynamics_trajectory_simulation():
    engine = MolecularDynamicsEngine()

    result = engine.simulate_trajectory(
        uniprot_id="Q9BYF1",
        system_name="PCSK9 Solvated Box",
        organism="Homo sapiens",
        forcefield="AMBER14SB",
        solvent_model="TIP3P",
        ensemble="NPT",
        total_duration_ns=100.0,
        total_frames=20,
        temperature_kelvin=300.0,
        pressure_bar=1.013,
    )

    assert isinstance(result, SimulationResult)
    assert result.system_name == "PCSK9 Solvated Box"
    assert result.total_duration_ns == 100.0
    assert result.equilibrium_rmsd_angstrom > 0.0

    # Frames verification
    assert len(result.trajectory_frames) == 20
    assert result.trajectory_frames[0].frame_index == 1
    assert "HEADER" in result.trajectory_frames[0].frame_pdb_coordinates
    assert "ATOM" in result.trajectory_frames[0].frame_pdb_coordinates

    # Residue Fluctuations verification
    assert len(result.residue_fluctuations) > 0
    has_flexible = any(r.is_flexible_loop for r in result.residue_fluctuations)
    assert has_flexible is True

    # Quantum Properties verification
    assert result.quantum_properties is not None
    assert result.quantum_properties.bandgap_energy_ev > 0.0
    assert result.quantum_properties.total_scf_energy_hartree < 0.0
    assert result.quantum_properties.dipole_moment_debye > 0.0


def test_generate_frame_pdb():
    engine = MolecularDynamicsEngine()
    pdb_str = engine.generate_frame_pdb(
        uniprot_id="Q9BYF1",
        system_name="PCSK9_Model",
        frame_idx=1,
        timestamp_ps=100.0,
        thermal_noise=0.2,
    )
    assert "HEADER" in pdb_str
    assert "ATOM" in pdb_str
    assert "END" in pdb_str
