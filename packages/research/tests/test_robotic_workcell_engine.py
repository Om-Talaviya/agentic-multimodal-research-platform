"""Tests for RoboticWorkcellEngine."""
import pytest
from research.robotics.workcell_engine import RoboticWorkcellEngine


def test_robotic_workcell_engine_opentrons():
    engine = RoboticWorkcellEngine()
    result = engine.compile_workcell_protocol(
        protocol_name="ELISA Reagent Dispense",
        platform="OPENTRONS_OT2",
        liquid_class="VISCOUS_GLYCEROL",
        samples_count=96,
        transfer_volume_ul=100.0,
    )

    assert "protocol" in result
    assert result["protocol"]["protocol_name"] == "ELISA Reagent Dispense"
    assert "opentrons" in result["protocol"]["compiled_python_script"]
    assert "delay" in result["protocol"]["compiled_python_script"]

    assert "deck_layout" in result
    assert len(result["deck_layout"]) == 4
    slots = [d["slot_number"] for d in result["deck_layout"]]
    assert 1 in slots
    assert 3 in slots

    assert "run_executions" in result
    assert result["run_executions"][0]["collision_check_passed"] is True
    assert result["run_executions"][0]["tips_consumed"] == 96


def test_robotic_workcell_engine_platforms():
    engine = RoboticWorkcellEngine()
    assert "OPENTRONS_OT2" in engine.PLATFORMS
    assert "HAMILTON_MICROLAB_STAR" in engine.PLATFORMS
    assert "WATER_FREE" in engine.LIQUID_CLASSES
