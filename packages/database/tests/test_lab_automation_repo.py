"""Tests for LabAutomationRepository (Phase 37)."""

import uuid
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from database.connection import Base
from database.models.user import User as DBUser
from database.repositories.lab_automation_repo import LabAutomationRepository


@pytest.fixture
async def test_db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_maker() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_lab_automation_repo_full_lifecycle(test_db_session: AsyncSession):
    repo = LabAutomationRepository(test_db_session)
    user_id = uuid.uuid4()

    # Create dummy user
    user = DBUser(id=user_id, username="test_roboticist", email="roboticist@synbio.org", password_hash="hash")
    test_db_session.add(user)
    await test_db_session.commit()

    # 1. Create Protocol
    protocol = await repo.create_protocol(
        user_id=user_id,
        protocol_name="CRISPR-Cas9 LNP High-Throughput Screening",
        robot_platform="Opentrons_OT2",
        assay_type="CRISPR_LNP_Formulation",
        total_runtime_minutes=14.2,
        liquid_waste_volume_ml=1.8,
        validation_status="valid",
        protocol_python_code="def run(ctx): pass",
    )
    assert protocol.id is not None
    assert protocol.protocol_name == "CRISPR-Cas9 LNP High-Throughput Screening"
    assert protocol.robot_platform == "Opentrons_OT2"

    # 2. Add Deck Slots
    slots = await repo.add_deck_slots(
        protocol_id=protocol.id,
        slots_data=[
            {"slot_number": 1, "labware_type": "opentrons_96_tiprack_300ul", "reagent_name": "300uL Tips", "initial_volume_ul": 0.0},
            {"slot_number": 2, "labware_type": "corning_96_wellplate_360ul_flat", "reagent_name": "Target Plate", "initial_volume_ul": 200.0},
        ],
    )
    assert len(slots) == 2
    assert slots[0].slot_number == 1
    assert slots[1].initial_volume_ul == 200.0

    # 3. Add Transfer Steps
    steps = await repo.add_transfer_steps(
        protocol_id=protocol.id,
        steps_data=[
            {"step_index": 1, "source_slot": 1, "source_well": "A1", "target_slot": 2, "target_well": "A1", "volume_ul": 25.0, "pipette_name": "p300_single_gen2", "liquid_class": "aqueous"},
            {"step_index": 2, "source_slot": 2, "source_well": "A1", "target_slot": 2, "target_well": "B1", "volume_ul": 50.0, "pipette_name": "p300_single_gen2", "liquid_class": "viscous_glycerol", "transfer_type": "mix"},
        ],
    )
    assert len(steps) == 2
    assert steps[1].transfer_type == "mix"

    # 4. Record Execution Trace
    trace = await repo.record_execution_trace(
        protocol_id=protocol.id,
        step_count=2,
        simulated_runtime_sec=852.0,
        estimated_tip_count=2,
        tip_waste_pct=2.1,
        collision_warnings=[],
        simulation_log=[{"step": 1, "action": "aspirate"}],
    )
    assert trace.id is not None
    assert trace.estimated_tip_count == 2

    # 5. Fetch Protocol with relations
    fetched = await repo.get_protocol(protocol.id)
    assert fetched is not None
    assert len(fetched.deck_slots) == 2
    assert len(fetched.transfer_steps) == 2
    assert len(fetched.execution_traces) == 1

    # 6. List Protocols
    listed = await repo.list_protocols(user_id=user_id)
    assert len(listed) == 1
    assert listed[0].id == protocol.id
