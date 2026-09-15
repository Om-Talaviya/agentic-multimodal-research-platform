"""Tests for RoboticProtocolCompiler (Phase 37)."""

import pytest
from research.robotic_protocol_compiler import (
    LabwareSlotSpec,
    RoboticProtocolCompiler,
    TransferStepSpec,
)


def test_compiler_opentrons_code_generation():
    compiler = RoboticProtocolCompiler()
    deck_slots = [
        LabwareSlotSpec(slot_number=1, labware_type="opentrons_96_tiprack_300ul", reagent_name="Tips"),
        LabwareSlotSpec(slot_number=2, labware_type="corning_96_wellplate_360ul_flat", reagent_name="Assay Plate", initial_volume_ul=100.0),
        LabwareSlotSpec(slot_number=3, labware_type="nest_12_reservoir_15ml", reagent_name="Buffer Reservoir", initial_volume_ul=10000.0),
    ]
    transfer_steps = [
        TransferStepSpec(step_index=1, source_slot=3, source_well="A1", target_slot=2, target_well="A1", volume_ul=30.0, liquid_class="viscous_glycerol"),
        TransferStepSpec(step_index=2, source_slot=2, source_well="A1", target_slot=2, target_well="B1", volume_ul=15.0, transfer_type="mix", liquid_class="aqueous"),
    ]

    compiled = compiler.compile_protocol(
        protocol_name="CRISPR OT-2 Automation",
        robot_platform="Opentrons_OT2",
        assay_type="CRISPR_LNP_Formulation",
        deck_slots=deck_slots,
        transfer_steps=transfer_steps,
    )

    assert compiled.protocol_name == "CRISPR OT-2 Automation"
    assert "from opentrons import protocol_api" in compiled.python_code
    assert 'metadata = {' in compiled.python_code
    assert 'requirements = {' in compiled.python_code
    assert "p300.pick_up_tip()" in compiled.python_code
    assert "p300.mix(" in compiled.python_code
    assert compiled.simulation_result.is_valid is True
    assert compiled.simulation_result.total_runtime_sec > 0.0
    assert len(compiled.simulation_result.simulation_log) == 2


def test_compiler_collision_and_underflow_detection():
    compiler = RoboticProtocolCompiler()
    deck_slots = [
        LabwareSlotSpec(slot_number=1, labware_type="opentrons_96_tiprack_300ul", initial_volume_ul=0.0),
        LabwareSlotSpec(slot_number=2, labware_type="corning_96_wellplate_360ul_flat", initial_volume_ul=10.0),  # Only 10uL available
        LabwareSlotSpec(slot_number=5, labware_type="opentrons_24_tuberack_generic_2ml_screwcap", initial_volume_ul=500.0),  # Tall labware in middle row
        LabwareSlotSpec(slot_number=8, labware_type="corning_96_wellplate_360ul_flat", initial_volume_ul=0.0),
    ]

    # Attempt to aspirate 50uL from slot 2 (which only has 10uL) and cross over slot 5 to slot 8
    transfer_steps = [
        TransferStepSpec(step_index=1, source_slot=2, source_well="A1", target_slot=8, target_well="A1", volume_ul=50.0),
    ]

    sim = compiler.simulate_deck_execution(deck_slots, transfer_steps)
    assert sim.is_valid is False  # Underflow critical error
    warning_types = [w.warning_type for w in sim.collision_warnings]
    assert "underflow_warning" in warning_types
    assert "height_hazard" in warning_types


def test_compiler_pylabrobot_and_autoprotocol():
    compiler = RoboticProtocolCompiler()
    compiled = compiler.compile_protocol(
        protocol_name="Universal Formulation",
        robot_platform="PyLabRobot_Universal",
    )

    assert "from pylabrobot.liquid_handling import LiquidHandler" in compiled.pylabrobot_code
    assert compiled.autoprotocol_json["format"] == "autoprotocol-v1.0"
    assert "instructions" in compiled.autoprotocol_json
    assert len(compiled.autoprotocol_json["refs"]) > 0
