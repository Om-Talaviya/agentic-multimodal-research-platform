"""Tests for RoboticWorkcellRepository."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from database.repositories.robotic_workcell_repo import RoboticWorkcellRepository


@pytest.mark.asyncio
async def test_robotic_workcell_repo_lifecycle(db_session: AsyncSession):
    repo = RoboticWorkcellRepository(db_session)

    # 1. Create Protocol
    proto = await repo.create_protocol(
        protocol_name="High-Throughput PCR Reaction Setup",
        robot_platform="OPENTRONS_OT2",
        target_liquid_class="WATER_FREE",
        total_aspirations_count=96,
        total_dispenses_count=96,
        compiled_python_script="def run(protocol): pass",
    )
    assert proto.id is not None
    assert proto.protocol_name == "High-Throughput PCR Reaction Setup"

    # 2. Add Deck Instruction
    slot = await repo.add_deck_instruction(
        protocol_id=proto.id,
        slot_number=1,
        labware_name="corning_96_wellplate_360ul_flat",
        labware_type="PLATE",
        initial_volume_ul=100.0,
    )
    assert slot.id is not None
    assert slot.slot_number == 1

    # 3. Add Run Execution
    exec_run = await repo.add_run_execution(
        protocol_id=proto.id,
        run_id_hash="RUN-OT2-9988",
        robot_serial_number="OT2-PROD-01",
        total_run_duration_seconds=320.0,
        tips_consumed=96,
        aspiration_accuracy_pct=99.8,
        collision_check_passed=True,
    )
    assert exec_run.id is not None
    assert exec_run.collision_check_passed is True

    # 4. Fetch Protocol
    fetched = await repo.get_protocol(proto.id)
    assert fetched is not None
    assert len(fetched.deck_layout) == 1
    assert len(fetched.run_executions) == 1

    # 5. List Protocols
    protos = await repo.list_protocols()
    assert len(protos) >= 1
