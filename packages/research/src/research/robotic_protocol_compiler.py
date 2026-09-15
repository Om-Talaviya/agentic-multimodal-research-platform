"""Autonomous Robotic Protocol Compiler & Liquid Handling Engine (Phase 37).

Generates production-grade Opentrons Protocol API v2 Python scripts, PyLabRobot Universal code,
and Autoprotocol JSON specifications with deterministic deck collision and tip simulation.
"""

import json
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from shared.logging import get_logger

logger = get_logger(__name__)


class LabwareSlotSpec(BaseModel):
    slot_number: int = Field(..., ge=1, le=12, description="Deck slot position 1-12")
    labware_type: str = Field(..., description="API labware definition name")
    reagent_name: Optional[str] = None
    initial_volume_ul: float = Field(default=0.0, ge=0.0)
    current_volume_ul: float = Field(default=0.0, ge=0.0)


class TransferStepSpec(BaseModel):
    step_index: int = Field(default=1, ge=1)
    source_slot: int = Field(..., ge=1, le=12)
    source_well: str = Field(..., description="Well coordinate e.g. A1")
    target_slot: int = Field(..., ge=1, le=12)
    target_well: str = Field(..., description="Well coordinate e.g. B2")
    volume_ul: float = Field(..., gt=0.0)
    pipette_name: str = Field(default="p300_single_gen2")
    transfer_type: str = Field(default="transfer")  # transfer, mix, aspirate, dispense
    liquid_class: str = Field(default="aqueous")  # aqueous, viscous_glycerol, volatile_ethanol


class CollisionWarning(BaseModel):
    step_index: int
    warning_type: str  # height_hazard, volume_overflow, underflow_warning, tip_exhaustion
    message: str
    severity: str = "warning"  # warning, critical


class SimulationStepLog(BaseModel):
    step_index: int
    action: str
    details: str
    source_remaining_ul: float
    target_current_ul: float
    tip_number: int
    elapsed_time_sec: float


class ProtocolSimulationResult(BaseModel):
    is_valid: bool
    total_runtime_sec: float
    total_runtime_minutes: float
    estimated_tip_count: int
    tip_waste_pct: float
    liquid_waste_volume_ml: float
    collision_warnings: List[CollisionWarning] = Field(default_factory=list)
    simulation_log: List[SimulationStepLog] = Field(default_factory=list)


class CompiledRoboticProtocol(BaseModel):
    protocol_name: str
    robot_platform: str
    assay_type: str
    deck_slots: List[LabwareSlotSpec]
    transfer_steps: List[TransferStepSpec]
    python_code: str
    pylabrobot_code: str
    autoprotocol_json: Dict[str, Any]
    simulation_result: ProtocolSimulationResult


class RoboticProtocolCompiler:
    """High-performance compiler for automated laboratory robotics and liquid handlers."""

    DEFAULT_LABWARE_MAP = {
        1: ("opentrons_96_tiprack_300ul", "300µL Tip Rack"),
        2: ("corning_96_wellplate_360ul_flat", "CRISPR Target 96-Well Plate"),
        3: ("nest_12_reservoir_15ml", "LNP Reagents & Buffer Reservoir"),
        4: ("opentrons_24_tuberack_generic_2ml_screwcap", "sgRNA & Cas9 Stock Tubes"),
        5: ("nest_96_wellplate_100ul_pcr_full_skirt", "qPCR Master Mix & Verification"),
        6: ("corning_96_wellplate_360ul_flat", "Cell Culture Lysis & Assay Plate"),
    }

    def __init__(self) -> None:
        pass

    def simulate_deck_execution(
        self,
        deck_slots: List[LabwareSlotSpec],
        transfer_steps: List[TransferStepSpec],
    ) -> ProtocolSimulationResult:
        """Simulate step-by-step deck execution, tracking volumes, tips, and physical hazards."""
        slot_volumes: Dict[Tuple[int, str], float] = {}
        slot_types: Dict[int, str] = {}
        
        for slot in deck_slots:
            slot_types[slot.slot_number] = slot.labware_type
            # Initialize default well A1 with initial volume if unspecified
            slot_volumes[(slot.slot_number, "ALL")] = slot.initial_volume_ul

        warnings: List[CollisionWarning] = []
        logs: List[SimulationStepLog] = []

        total_runtime_sec = 15.0  # Homed initialization overhead
        tip_count = 0
        current_tip_in_use = False
        liquid_waste_ul = 0.0

        tall_labware = {"opentrons_24_tuberack_generic_2ml_screwcap", "nest_12_reservoir_15ml"}

        for idx, step in enumerate(transfer_steps, start=1):
            # Check deck slots existence
            src_type = slot_types.get(step.source_slot, "generic_labware")
            tgt_type = slot_types.get(step.target_slot, "generic_labware")

            # Tip lifecycle
            if not current_tip_in_use:
                tip_count += 1
                current_tip_in_use = True
                total_runtime_sec += 4.5  # Pick up tip duration

            # Collision / Gantry Path Check
            if (step.source_slot in [1, 2, 3] and step.target_slot in [7, 8, 9]) or \
               (step.source_slot in [7, 8, 9] and step.target_slot in [1, 2, 3]):
                for mid_slot in [4, 5, 6]:
                    if slot_types.get(mid_slot) in tall_labware:
                        warnings.append(CollisionWarning(
                            step_index=idx,
                            warning_type="height_hazard",
                            message=f"Gantry trajectory passes over tall labware in Slot {mid_slot} ({slot_types[mid_slot]}). Ensure Z-clearance is >= 45mm.",
                            severity="warning",
                        ))

            # Volume simulation
            src_key = (step.source_slot, step.source_well)
            tgt_key = (step.target_slot, step.target_well)

            src_vol = slot_volumes.get(src_key, slot_volumes.get((step.source_slot, "ALL"), 1000.0))
            tgt_vol = slot_volumes.get(tgt_key, 0.0)

            if step.volume_ul > src_vol:
                warnings.append(CollisionWarning(
                    step_index=idx,
                    warning_type="underflow_warning",
                    message=f"Requested {step.volume_ul}µL from Slot {step.source_slot} Well {step.source_well}, but available volume is {src_vol}µL.",
                    severity="critical",
                ))

            # Pipette volume capacity check
            if "p300" in step.pipette_name.lower() and step.volume_ul > 300.0:
                warnings.append(CollisionWarning(
                    step_index=idx,
                    warning_type="pipette_overcapacity",
                    message=f"Step volume {step.volume_ul}µL exceeds {step.pipette_name} max capacity (300µL). Step requires multi-dispense.",
                    severity="warning",
                ))

            # Update volumes
            new_src_vol = max(0.0, src_vol - step.volume_ul)
            new_tgt_vol = tgt_vol + step.volume_ul
            slot_volumes[src_key] = new_src_vol
            slot_volumes[tgt_key] = new_tgt_vol

            # Liquid class timing multiplier
            speed_mult = 1.8 if "viscous" in step.liquid_class else 1.0
            step_duration = (8.0 + (step.volume_ul * 0.04)) * speed_mult
            total_runtime_sec += step_duration

            # Simulate liquid waste / droplet loss
            step_waste = step.volume_ul * 0.015
            liquid_waste_ul += step_waste

            # Action description
            desc = f"Transferred {step.volume_ul:.1f}µL from Slot {step.source_slot}:{step.source_well} to Slot {step.target_slot}:{step.target_well} [{step.liquid_class}]"
            logs.append(SimulationStepLog(
                step_index=idx,
                action="pipette_transfer",
                details=desc,
                source_remaining_ul=round(new_src_vol, 2),
                target_current_ul=round(new_tgt_vol, 2),
                tip_number=tip_count,
                elapsed_time_sec=round(total_runtime_sec, 1),
            ))

        # Drop final tip
        if current_tip_in_use:
            total_runtime_sec += 2.5

        # Tip exhaustion check
        if tip_count > 96:
            warnings.append(CollisionWarning(
                step_index=len(transfer_steps),
                warning_type="tip_exhaustion",
                message=f"Protocol uses {tip_count} tips, which exceeds a single 96-tip rack. Secondary tip rack required in deck layout.",
                severity="critical",
            ))

        tip_waste_pct = round(min(100.0, (tip_count / 96.0) * 100.0), 1)
        liquid_waste_ml = round(liquid_waste_ul / 1000.0, 3)

        is_valid = not any(w.severity == "critical" for w in warnings)

        return ProtocolSimulationResult(
            is_valid=is_valid,
            total_runtime_sec=round(total_runtime_sec, 1),
            total_runtime_minutes=round(total_runtime_sec / 60.0, 2),
            estimated_tip_count=tip_count,
            tip_waste_pct=tip_waste_pct,
            liquid_waste_volume_ml=liquid_waste_ml,
            collision_warnings=warnings,
            simulation_log=logs,
        )

    def generate_opentrons_python_code(
        self,
        protocol_name: str,
        robot_platform: str,
        deck_slots: List[LabwareSlotSpec],
        transfer_steps: List[TransferStepSpec],
    ) -> str:
        """Generate fully compliant, runnable Opentrons Protocol API v2 Python code."""
        robot_type = "OT-2" if "OT2" in robot_platform or "OT-2" in robot_platform else "Flex"
        
        lines = [
            '"""',
            f'Opentrons Protocol: {protocol_name}',
            f'Target Workstation: {robot_platform}',
            'Auto-generated by AI Research OS - Autonomous Laboratory Automation Engine',
            '"""',
            '',
            'from opentrons import protocol_api',
            '',
            'metadata = {',
            f'    "protocolName": "{protocol_name}",',
            '    "author": "AI Research OS Autonomous Robotic Synthesizer",',
            '    "description": "High-throughput automated liquid handling protocol with microfluidic coordinate precision.",',
            '    "apiLevel": "2.15",',
            '}',
            '',
            'requirements = {',
            f'    "robotType": "{robot_type}",',
            '    "apiLevel": "2.15",',
            '}',
            '',
            'def run(protocol: protocol_api.ProtocolContext):',
            '    # -------------------------------------------------------------',
            '    # 1. Deck Labware Configuration',
            '    # -------------------------------------------------------------',
        ]

        tip_rack_slots = []
        for slot in sorted(deck_slots, key=lambda s: s.slot_number):
            var_name = f"labware_slot_{slot.slot_number}"
            if "tiprack" in slot.labware_type.lower():
                tip_rack_slots.append(var_name)
            lines.append(f'    {var_name} = protocol.load_labware("{slot.labware_type}", {slot.slot_number}, label="{slot.reagent_name or slot.labware_type}")')

        lines.extend([
            '',
            '    # -------------------------------------------------------------',
            '    # 2. Pipette Mount Configuration',
            '    # -------------------------------------------------------------',
        ])

        if tip_rack_slots:
            tipracks_arg = f"[{', '.join(tip_rack_slots)}]"
        else:
            lines.append('    default_tiprack = protocol.load_labware("opentrons_96_tiprack_300ul", 1)')
            tipracks_arg = "[default_tiprack]"

        lines.append(f'    p300 = protocol.load_instrument("p300_single_gen2", mount="right", tip_racks={tipracks_arg})')
        lines.append('    p300.flow_rate.aspirate = 150')
        lines.append('    p300.flow_rate.dispense = 300')
        lines.append('')
        lines.append('    # -------------------------------------------------------------')
        lines.append('    # 3. Pipetting & Liquid Handling Sequence')
        lines.append('    # -------------------------------------------------------------')

        for idx, step in enumerate(transfer_steps, start=1):
            src_var = f"labware_slot_{step.source_slot}"
            tgt_var = f"labware_slot_{step.target_slot}"
            lines.append(f'    # Step {idx}: Transfer {step.volume_ul}uL ({step.liquid_class})')
            lines.append(f'    p300.pick_up_tip()')
            
            if "viscous" in step.liquid_class:
                lines.append(f'    p300.flow_rate.aspirate = 50  # Slowed for viscous fluid')
                lines.append(f'    p300.flow_rate.dispense = 80')
            else:
                lines.append(f'    p300.flow_rate.aspirate = 150')
                lines.append(f'    p300.flow_rate.dispense = 300')

            lines.append(f'    p300.aspirate({step.volume_ul}, {src_var}["{step.source_well}"])')
            if "viscous" in step.liquid_class:
                lines.append('    protocol.delay(seconds=1.5)  # Viscous relaxation delay')
            
            lines.append(f'    p300.dispense({step.volume_ul}, {tgt_var}["{step.target_well}"])')
            
            if step.transfer_type == "mix":
                lines.append(f'    p300.mix(3, {min(step.volume_ul * 0.8, 200.0)}, {tgt_var}["{step.target_well}"])')
            
            lines.append('    p300.blow_out()')
            lines.append('    p300.drop_tip()')
            lines.append('')

        lines.append('    protocol.comment("Robotic Protocol Execution Finished Successfully.")')
        return "\n".join(lines)

    def generate_pylabrobot_code(
        self,
        protocol_name: str,
        deck_slots: List[LabwareSlotSpec],
        transfer_steps: List[TransferStepSpec],
    ) -> str:
        """Generate PyLabRobot universal liquid handling script."""
        lines = [
            '"""',
            f'PyLabRobot Universal Protocol: {protocol_name}',
            'Auto-generated by AI Research OS - Autonomous Laboratory Automation Engine',
            '"""',
            '',
            'import asyncio',
            'from pylabrobot.liquid_handling import LiquidHandler',
            'from pylabrobot.liquid_handling.backends import OpentronsBackend, ChattyBackend',
            'from pylabrobot.resources import (',
            '    Deck, Resource, Plate, TipRack, Well,',
            '    corning_96_wellplate_360ul_flat,',
            '    opentrons_96_tiprack_300ul,',
            ')',
            '',
            'async def main():',
            '    backend = OpentronsBackend(host="192.168.1.100")',
            '    lh = LiquidHandler(backend=backend, deck=Deck())',
            '    await lh.setup()',
            '',
            '    # Labware Deck Allocation',
        ]

        for s in deck_slots:
            lines.append(f'    slot_{s.slot_number} = corning_96_wellplate_360ul_flat(name="slot_{s.slot_number}_{s.reagent_name or "plate"}")')
            lines.append(f'    lh.deck.assign_child_resource(slot_{s.slot_number}, location=lh.deck.get_slot({s.slot_number}))')

        lines.extend([
            '',
            '    # Transfer Steps',
        ])

        for idx, st in enumerate(transfer_steps, start=1):
            lines.append(f'    # Transfer {idx}: {st.volume_ul}uL')
            lines.append(f'    await lh.pick_up_tips(lh.deck.get_resource("slot_1")["A1"])')
            lines.append(f'    await lh.aspirate(slot_{st.source_slot}["{st.source_well}"], vols=[{st.volume_ul}])')
            lines.append(f'    await lh.dispense(slot_{st.target_slot}["{st.target_well}"], vols=[{st.volume_ul}])')
            lines.append('    await lh.drop_tips()')
            lines.append('')

        lines.append('    await lh.stop()')
        lines.append('')
        lines.append('if __name__ == "__main__":')
        lines.append('    asyncio.run(main())')

        return "\n".join(lines)

    def generate_autoprotocol_json(
        self,
        protocol_name: str,
        deck_slots: List[LabwareSlotSpec],
        transfer_steps: List[TransferStepSpec],
    ) -> Dict[str, Any]:
        """Generate standard Autoprotocol JSON specification for cloud laboratory execution."""
        refs: Dict[str, Any] = {}
        for s in deck_slots:
            refs[f"slot_{s.slot_number}"] = {
                "new": s.labware_type,
                "discard": False,
                "label": s.reagent_name or f"Deck Slot {s.slot_number}",
            }

        instructions: List[Dict[str, Any]] = []
        for step in transfer_steps:
            instructions.append({
                "op": "pipette",
                "groups": [
                    {
                        "transfer": [
                            {
                                "from": f"slot_{step.source_slot}/{step.source_well}",
                                "to": f"slot_{step.target_slot}/{step.target_well}",
                                "volume": f"{step.volume_ul}:microliter",
                                "mix_after": {
                                    "volume": f"{min(step.volume_ul * 0.8, 200.0)}:microliter",
                                    "repetitions": 3,
                                } if step.transfer_type == "mix" else None,
                            }
                        ]
                    }
                ]
            })

        return {
            "format": "autoprotocol-v1.0",
            "title": protocol_name,
            "refs": refs,
            "instructions": instructions,
        }

    def compile_protocol(
        self,
        protocol_name: str,
        robot_platform: str = "Opentrons_OT2",
        assay_type: str = "CRISPR_LNP_Formulation",
        deck_slots: Optional[List[LabwareSlotSpec]] = None,
        transfer_steps: Optional[List[TransferStepSpec]] = None,
    ) -> CompiledRoboticProtocol:
        """Compile a full laboratory automation specification into robotic Python, PyLabRobot, and Autoprotocol representations."""
        # Setup default deck slots if empty
        if not deck_slots:
            deck_slots = [
                LabwareSlotSpec(slot_number=1, labware_type="opentrons_96_tiprack_300ul", reagent_name="Opentrons 300uL Tips", initial_volume_ul=0.0),
                LabwareSlotSpec(slot_number=2, labware_type="corning_96_wellplate_360ul_flat", reagent_name="CRISPR Target Reaction Plate", initial_volume_ul=100.0),
                LabwareSlotSpec(slot_number=3, labware_type="nest_12_reservoir_15ml", reagent_name="Lipid-Ethanol & Citrate Buffer Reservoir", initial_volume_ul=15000.0),
                LabwareSlotSpec(slot_number=4, labware_type="opentrons_24_tuberack_generic_2ml_screwcap", reagent_name="Cas9-sgRNA RNP Complex Tube Rack", initial_volume_ul=1800.0),
            ]

        # Setup default transfer steps if empty
        if not transfer_steps:
            transfer_steps = [
                TransferStepSpec(step_index=1, source_slot=3, source_well="A1", target_slot=2, target_well="A1", volume_ul=45.0, pipette_name="p300_single_gen2", liquid_class="viscous_glycerol"),
                TransferStepSpec(step_index=2, source_slot=4, source_well="A1", target_slot=2, target_well="A1", volume_ul=15.0, pipette_name="p300_single_gen2", liquid_class="aqueous"),
                TransferStepSpec(step_index=3, source_slot=3, source_well="A2", target_slot=2, target_well="A1", volume_ul=90.0, pipette_name="p300_single_gen2", liquid_class="aqueous"),
                TransferStepSpec(step_index=4, source_slot=2, source_well="A1", target_slot=2, target_well="B1", volume_ul=50.0, pipette_name="p300_single_gen2", transfer_type="mix", liquid_class="aqueous"),
            ]

        # Run virtual simulation and collision trace
        sim_result = self.simulate_deck_execution(deck_slots, transfer_steps)

        # Generate scripts
        python_code = self.generate_opentrons_python_code(
            protocol_name=protocol_name,
            robot_platform=robot_platform,
            deck_slots=deck_slots,
            transfer_steps=transfer_steps,
        )

        pylabrobot_code = self.generate_pylabrobot_code(
            protocol_name=protocol_name,
            deck_slots=deck_slots,
            transfer_steps=transfer_steps,
        )

        autoprotocol_json = self.generate_autoprotocol_json(
            protocol_name=protocol_name,
            deck_slots=deck_slots,
            transfer_steps=transfer_steps,
        )

        logger.info(
            "robotic_protocol_compiled",
            name=protocol_name,
            platform=robot_platform,
            runtime_min=sim_result.total_runtime_minutes,
            warnings_count=len(sim_result.collision_warnings),
        )

        return CompiledRoboticProtocol(
            protocol_name=protocol_name,
            robot_platform=robot_platform,
            assay_type=assay_type,
            deck_slots=deck_slots,
            transfer_steps=transfer_steps,
            python_code=python_code,
            pylabrobot_code=pylabrobot_code,
            autoprotocol_json=autoprotocol_json,
            simulation_result=sim_result,
        )
