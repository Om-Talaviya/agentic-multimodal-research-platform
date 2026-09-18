"""API Routes for Laboratory Robotics Automation & Self-Driving Workcell Protocol Compiler."""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db, get_current_user
from database.repositories.robotic_workcell_repo import RoboticWorkcellRepository
from research.robotics.workcell_engine import RoboticWorkcellEngine

router = APIRouter(prefix="/robotic-workcell", tags=["Robotic Workcell & Lab Automation"])


class ProtocolCompileRequest(BaseModel):
    protocol_name: str = Field(..., description="Protocol display title")
    platform: str = Field(default="OPENTRONS_OT2", description="Platform: OPENTRONS_OT2, HAMILTON_MICROLAB_STAR, TECAN_FLUENT, BIOX_3D_BIOPRINTER")
    liquid_class: str = Field(default="WATER_FREE", description="Liquid class: WATER_FREE, VISCOUS_GLYCEROL, ETHANOL_VOLATILE, BLOOD_PLASMA")
    samples_count: int = Field(default=96, ge=1, le=384)
    transfer_volume_ul: float = Field(default=50.0, ge=1.0, le=1000.0)


@router.get("/platforms")
async def get_supported_platforms():
    """List supported robotic liquid handlers and liquid classes."""
    return {
        "platforms": RoboticWorkcellEngine.PLATFORMS,
        "liquid_classes": RoboticWorkcellEngine.LIQUID_CLASSES,
    }


@router.post("/compile", status_code=status.HTTP_201_CREATED)
async def compile_robotic_protocol(
    request: ProtocolCompileRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Compile laboratory automation instructions into executable Python protocols and check deck collisions."""
    engine = RoboticWorkcellEngine()
    result = engine.compile_workcell_protocol(
        protocol_name=request.protocol_name,
        platform=request.platform,
        liquid_class=request.liquid_class,
        samples_count=request.samples_count,
        transfer_volume_ul=request.transfer_volume_ul,
    )

    repo = RoboticWorkcellRepository(db)
    p_info = result["protocol"]
    protocol = await repo.create_protocol(
        protocol_name=p_info["protocol_name"],
        robot_platform=p_info["robot_platform"],
        target_liquid_class=p_info["target_liquid_class"],
        total_aspirations_count=p_info["total_aspirations_count"],
        total_dispenses_count=p_info["total_dispenses_count"],
        compiled_python_script=p_info["compiled_python_script"],
        execution_status=p_info["execution_status"],
    )

    for slot in result["deck_layout"]:
        await repo.add_deck_instruction(
            protocol_id=protocol.id,
            slot_number=slot["slot_number"],
            labware_name=slot["labware_name"],
            labware_type=slot["labware_type"],
            initial_volume_ul=slot["initial_volume_ul"],
        )

    for run in result["run_executions"]:
        await repo.add_run_execution(
            protocol_id=protocol.id,
            run_id_hash=run["run_id_hash"],
            robot_serial_number=run["robot_serial_number"],
            total_run_duration_seconds=run["total_run_duration_seconds"],
            tips_consumed=run["tips_consumed"],
            aspiration_accuracy_pct=run["aspiration_accuracy_pct"],
            collision_check_passed=run["collision_check_passed"],
            run_log_text=run["run_log_text"],
        )

    saved = await repo.get_protocol(protocol.id)
    return {
        "status": "success",
        "id": protocol.id,
        "protocol_name": protocol.protocol_name,
        "robot_platform": protocol.robot_platform,
        "target_liquid_class": protocol.target_liquid_class,
        "deck_layout_count": len(saved.deck_layout if saved else []),
        "run_executions_count": len(saved.run_executions if saved else []),
        "script_preview": protocol.compiled_python_script[:150] + "...",
    }


@router.get("/protocols")
async def list_robotic_protocols(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """List recent compiled robotic workcell protocols."""
    repo = RoboticWorkcellRepository(db)
    protocols = await repo.list_protocols(limit=limit)
    return [
        {
            "id": p.id,
            "protocol_name": p.protocol_name,
            "robot_platform": p.robot_platform,
            "target_liquid_class": p.target_liquid_class,
            "total_aspirations_count": p.total_aspirations_count,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "deck_layout_count": len(p.deck_layout),
            "run_executions_count": len(p.run_executions),
        }
        for p in protocols
    ]


@router.get("/protocols/{protocol_id}")
async def get_robotic_protocol(
    protocol_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    """Get complete details, full Python script, and deck layouts for a protocol."""
    repo = RoboticWorkcellRepository(db)
    proto = await repo.get_protocol(protocol_id)
    if not proto:
        raise HTTPException(status_code=404, detail="Protocol not found")

    return {
        "id": proto.id,
        "protocol_name": proto.protocol_name,
        "robot_platform": proto.robot_platform,
        "target_liquid_class": proto.target_liquid_class,
        "total_aspirations_count": proto.total_aspirations_count,
        "total_dispenses_count": proto.total_dispenses_count,
        "compiled_python_script": proto.compiled_python_script,
        "deck_layout": [
            {
                "id": d.id,
                "slot_number": d.slot_number,
                "labware_name": d.labware_name,
                "labware_type": d.labware_type,
                "initial_volume_ul": d.initial_volume_ul,
            }
            for d in proto.deck_layout
        ],
        "run_executions": [
            {
                "id": r.id,
                "run_id_hash": r.run_id_hash,
                "robot_serial_number": r.robot_serial_number,
                "total_run_duration_seconds": r.total_run_duration_seconds,
                "tips_consumed": r.tips_consumed,
                "aspiration_accuracy_pct": r.aspiration_accuracy_pct,
                "collision_check_passed": r.collision_check_passed,
                "run_log_text": r.run_log_text,
            }
            for r in proto.run_executions
        ],
    }
