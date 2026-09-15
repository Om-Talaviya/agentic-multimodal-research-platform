"""Autonomous Laboratory Automation & Robotic Protocol API Routes (Phase 37)."""

import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user, get_db_session
from database.models.user import User as DBUser
from database.repositories.lab_automation_repo import LabAutomationRepository
from research.robotic_protocol_compiler import (
    LabwareSlotSpec,
    RoboticProtocolCompiler,
    TransferStepSpec,
)
from shared.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/lab", tags=["lab-automation"])
compiler = RoboticProtocolCompiler()


# --- Pydantic Request / Response Schemas ---

class ProtocolCompileRequest(BaseModel):
    protocol_name: str = Field(..., description="Descriptive protocol title")
    robot_platform: str = Field("Opentrons_OT2", description="Opentrons_OT2, Opentrons_Flex, PyLabRobot_Universal, Tecan_Fluent, Hamilton_STAR")
    assay_type: str = Field("CRISPR_LNP_Formulation", description="CRISPR_LNP_Formulation, qPCR_Assay, ELISA_Screening, Serial_Dilution, PCR_MasterMix")
    deck_slots: Optional[List[LabwareSlotSpec]] = None
    transfer_steps: Optional[List[TransferStepSpec]] = None
    workspace_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None


class ProtocolSimulateRequest(BaseModel):
    transfer_steps: Optional[List[TransferStepSpec]] = None


# --- Endpoint Implementations ---

@router.post("/protocols/compile", status_code=status.HTTP_201_CREATED)
async def compile_robotic_protocol(
    payload: ProtocolCompileRequest,
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Autonomous Compilation & Virtual Validation of Robotic Liquid Handling Protocols."""
    compiled = compiler.compile_protocol(
        protocol_name=payload.protocol_name,
        robot_platform=payload.robot_platform,
        assay_type=payload.assay_type,
        deck_slots=payload.deck_slots,
        transfer_steps=payload.transfer_steps,
    )

    repo = LabAutomationRepository(session)
    validation_status = "valid" if compiled.simulation_result.is_valid else "collision_detected"

    protocol = await repo.create_protocol(
        user_id=current_user.id,
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
        protocol_name=payload.protocol_name,
        robot_platform=payload.robot_platform,
        assay_type=payload.assay_type,
        deck_layout_json={"slots": [s.model_dump() for s in compiled.deck_slots]},
        total_runtime_minutes=compiled.simulation_result.total_runtime_minutes,
        liquid_waste_volume_ml=compiled.simulation_result.liquid_waste_volume_ml,
        validation_status=validation_status,
        protocol_python_code=compiled.python_code,
        autoprotocol_json=compiled.autoprotocol_json,
    )

    # Persist deck slots
    await repo.add_deck_slots(
        protocol_id=protocol.id,
        slots_data=[s.model_dump() for s in compiled.deck_slots],
    )

    # Persist transfer steps
    await repo.add_transfer_steps(
        protocol_id=protocol.id,
        steps_data=[st.model_dump() for st in compiled.transfer_steps],
    )

    # Persist initial execution trace
    await repo.record_execution_trace(
        protocol_id=protocol.id,
        step_count=len(compiled.transfer_steps),
        simulated_runtime_sec=compiled.simulation_result.total_runtime_sec,
        estimated_tip_count=compiled.simulation_result.estimated_tip_count,
        tip_waste_pct=compiled.simulation_result.tip_waste_pct,
        collision_warnings=[w.model_dump() for w in compiled.simulation_result.collision_warnings],
        simulation_log=[log.model_dump() for log in compiled.simulation_result.simulation_log],
    )

    await session.commit()
    logger.info("robotic_protocol_persisted", protocol_id=str(protocol.id), name=protocol.protocol_name)

    return {
        "id": str(protocol.id),
        "protocol_name": protocol.protocol_name,
        "robot_platform": protocol.robot_platform,
        "assay_type": protocol.assay_type,
        "validation_status": protocol.validation_status,
        "total_runtime_minutes": protocol.total_runtime_minutes,
        "liquid_waste_volume_ml": protocol.liquid_waste_volume_ml,
        "protocol_python_code": protocol.protocol_python_code,
        "pylabrobot_code": compiled.pylabrobot_code,
        "autoprotocol_json": protocol.autoprotocol_json,
        "deck_slots": [s.model_dump() for s in compiled.deck_slots],
        "transfer_steps": [st.model_dump() for st in compiled.transfer_steps],
        "simulation_result": compiled.simulation_result.model_dump(),
        "created_at": protocol.created_at.isoformat(),
    }


@router.get("/protocols")
async def list_robotic_protocols(
    robot_platform: Optional[str] = Query(None, description="Filter by robot platform"),
    workspace_id: Optional[uuid.UUID] = Query(None),
    project_id: Optional[uuid.UUID] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> List[Dict[str, Any]]:
    """List robotic protocols with deck slots, transfer steps, and telemetry."""
    repo = LabAutomationRepository(session)
    protocols = await repo.list_protocols(
        user_id=current_user.id,
        workspace_id=workspace_id,
        project_id=project_id,
        robot_platform=robot_platform,
        limit=limit,
        offset=offset,
    )

    return [
        {
            "id": str(p.id),
            "protocol_name": p.protocol_name,
            "robot_platform": p.robot_platform,
            "assay_type": p.assay_type,
            "validation_status": p.validation_status,
            "total_runtime_minutes": p.total_runtime_minutes,
            "liquid_waste_volume_ml": p.liquid_waste_volume_ml,
            "deck_slots_count": len(p.deck_slots),
            "transfer_steps_count": len(p.transfer_steps),
            "execution_traces_count": len(p.execution_traces),
            "created_at": p.created_at.isoformat(),
        }
        for p in protocols
    ]


@router.get("/protocols/{protocol_id}")
async def get_robotic_protocol(
    protocol_id: uuid.UUID,
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Fetch complete robotic protocol details including slots, transfer steps, and simulation traces."""
    repo = LabAutomationRepository(session)
    protocol = await repo.get_protocol(protocol_id)
    if not protocol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Robotic protocol '{protocol_id}' not found.",
        )

    return {
        "id": str(protocol.id),
        "protocol_name": protocol.protocol_name,
        "robot_platform": protocol.robot_platform,
        "assay_type": protocol.assay_type,
        "validation_status": protocol.validation_status,
        "total_runtime_minutes": protocol.total_runtime_minutes,
        "liquid_waste_volume_ml": protocol.liquid_waste_volume_ml,
        "protocol_python_code": protocol.protocol_python_code,
        "autoprotocol_json": protocol.autoprotocol_json,
        "deck_slots": [
            {
                "id": str(s.id),
                "slot_number": s.slot_number,
                "labware_type": s.labware_type,
                "reagent_name": s.reagent_name,
                "initial_volume_ul": s.initial_volume_ul,
                "current_volume_ul": s.current_volume_ul,
            }
            for s in protocol.deck_slots
        ],
        "transfer_steps": [
            {
                "id": str(st.id),
                "step_index": st.step_index,
                "source_slot": st.source_slot,
                "source_well": st.source_well,
                "target_slot": st.target_slot,
                "target_well": st.target_well,
                "volume_ul": st.volume_ul,
                "pipette_name": st.pipette_name,
                "transfer_type": st.transfer_type,
                "liquid_class": st.liquid_class,
            }
            for st in protocol.transfer_steps
        ],
        "execution_traces": [
            {
                "id": str(t.id),
                "step_count": t.step_count,
                "simulated_runtime_sec": t.simulated_runtime_sec,
                "estimated_tip_count": t.estimated_tip_count,
                "tip_waste_pct": t.tip_waste_pct,
                "collision_warnings": t.collision_warnings,
                "simulation_log": t.simulation_log,
                "executed_at": t.executed_at.isoformat(),
            }
            for t in protocol.execution_traces
        ],
        "created_at": protocol.created_at.isoformat(),
    }


@router.post("/protocols/{protocol_id}/simulate")
async def simulate_protocol(
    protocol_id: uuid.UUID,
    payload: ProtocolSimulateRequest,
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Dict[str, Any]:
    """Execute dynamic deck collision check and pipetting physics simulation."""
    repo = LabAutomationRepository(session)
    protocol = await repo.get_protocol(protocol_id)
    if not protocol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Robotic protocol '{protocol_id}' not found.",
        )

    deck_slots = [
        LabwareSlotSpec(
            slot_number=s.slot_number,
            labware_type=s.labware_type,
            reagent_name=s.reagent_name,
            initial_volume_ul=s.initial_volume_ul,
            current_volume_ul=s.current_volume_ul,
        )
        for s in protocol.deck_slots
    ]

    transfer_steps = payload.transfer_steps or [
        TransferStepSpec(
            step_index=st.step_index,
            source_slot=st.source_slot,
            source_well=st.source_well,
            target_slot=st.target_slot,
            target_well=st.target_well,
            volume_ul=st.volume_ul,
            pipette_name=st.pipette_name,
            transfer_type=st.transfer_type,
            liquid_class=st.liquid_class,
        )
        for st in protocol.transfer_steps
    ]

    sim_result = compiler.simulate_deck_execution(deck_slots, transfer_steps)

    # Record execution trace
    trace = await repo.record_execution_trace(
        protocol_id=protocol.id,
        step_count=len(transfer_steps),
        simulated_runtime_sec=sim_result.total_runtime_sec,
        estimated_tip_count=sim_result.estimated_tip_count,
        tip_waste_pct=sim_result.tip_waste_pct,
        collision_warnings=[w.model_dump() for w in sim_result.collision_warnings],
        simulation_log=[log.model_dump() for log in sim_result.simulation_log],
    )

    await session.commit()

    return {
        "trace_id": str(trace.id),
        "protocol_id": str(protocol.id),
        "simulation_result": sim_result.model_dump(),
    }


@router.get("/protocols/{protocol_id}/export-code")
async def export_protocol_code(
    protocol_id: uuid.UUID,
    format: str = Query("opentrons_python", description="opentrons_python, pylabrobot, autoprotocol"),
    current_user: DBUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Any:
    """Export executable Python robot script or Autoprotocol JSON."""
    repo = LabAutomationRepository(session)
    protocol = await repo.get_protocol(protocol_id)
    if not protocol:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Robotic protocol '{protocol_id}' not found.",
        )

    if format == "autoprotocol":
        return protocol.autoprotocol_json
    elif format == "pylabrobot":
        deck_slots = [
            LabwareSlotSpec(
                slot_number=s.slot_number,
                labware_type=s.labware_type,
                reagent_name=s.reagent_name,
                initial_volume_ul=s.initial_volume_ul,
            )
            for s in protocol.deck_slots
        ]
        transfer_steps = [
            TransferStepSpec(
                step_index=st.step_index,
                source_slot=st.source_slot,
                source_well=st.source_well,
                target_slot=st.target_slot,
                target_well=st.target_well,
                volume_ul=st.volume_ul,
                pipette_name=st.pipette_name,
                transfer_type=st.transfer_type,
                liquid_class=st.liquid_class,
            )
            for st in protocol.transfer_steps
        ]
        pylabrobot_code = compiler.generate_pylabrobot_code(
            protocol_name=protocol.protocol_name,
            deck_slots=deck_slots,
            transfer_steps=transfer_steps,
        )
        return Response(content=pylabrobot_code, media_type="text/x-python")
    else:
        return Response(content=protocol.protocol_python_code, media_type="text/x-python")
