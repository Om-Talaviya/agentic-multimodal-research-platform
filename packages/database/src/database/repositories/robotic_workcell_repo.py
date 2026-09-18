"""Repository for Laboratory Robotics Automation & Workcell Protocols."""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.robotic_workcell import (
    DBRoboticWorkcellProtocol,
    DBDeckLayoutInstruction,
    DBAutomatedRunExecution,
)


class RoboticWorkcellRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_protocol(
        self,
        protocol_name: str,
        robot_platform: str = "OPENTRONS_OT2",
        target_liquid_class: str = "WATER_FREE",
        total_aspirations_count: int = 96,
        total_dispenses_count: int = 96,
        compiled_python_script: str = "",
        execution_status: str = "COMPILED",
        protocol_metadata_json: Optional[Dict[str, Any]] = None,
    ) -> DBRoboticWorkcellProtocol:
        proto = DBRoboticWorkcellProtocol(
            protocol_name=protocol_name,
            robot_platform=robot_platform,
            target_liquid_class=target_liquid_class,
            total_aspirations_count=total_aspirations_count,
            total_dispenses_count=total_dispenses_count,
            compiled_python_script=compiled_python_script,
            execution_status=execution_status,
            protocol_metadata_json=protocol_metadata_json or {},
        )
        self.session.add(proto)
        await self.session.commit()
        await self.session.refresh(proto)
        return proto

    async def add_deck_instruction(
        self,
        protocol_id: str,
        slot_number: int = 1,
        labware_name: str = "corning_96_wellplate_360ul_flat",
        labware_type: str = "PLATE",
        initial_volume_ul: float = 200.0,
    ) -> DBDeckLayoutInstruction:
        instr = DBDeckLayoutInstruction(
            protocol_id=protocol_id,
            slot_number=slot_number,
            labware_name=labware_name,
            labware_type=labware_type,
            initial_volume_ul=initial_volume_ul,
        )
        self.session.add(instr)
        await self.session.commit()
        await self.session.refresh(instr)
        return instr

    async def add_run_execution(
        self,
        protocol_id: str,
        run_id_hash: str,
        robot_serial_number: str = "OT2-PROD-WORKCELL-01",
        total_run_duration_seconds: float = 345.0,
        tips_consumed: int = 96,
        aspiration_accuracy_pct: float = 99.4,
        collision_check_passed: bool = True,
        run_log_text: str = "",
    ) -> DBAutomatedRunExecution:
        exec_run = DBAutomatedRunExecution(
            protocol_id=protocol_id,
            run_id_hash=run_id_hash,
            robot_serial_number=robot_serial_number,
            total_run_duration_seconds=total_run_duration_seconds,
            tips_consumed=tips_consumed,
            aspiration_accuracy_pct=aspiration_accuracy_pct,
            collision_check_passed=collision_check_passed,
            run_log_text=run_log_text,
        )
        self.session.add(exec_run)
        await self.session.commit()
        await self.session.refresh(exec_run)
        return exec_run

    async def get_protocol(self, protocol_id: str) -> Optional[DBRoboticWorkcellProtocol]:
        stmt = (
            select(DBRoboticWorkcellProtocol)
            .where(DBRoboticWorkcellProtocol.id == protocol_id)
            .options(
                selectinload(DBRoboticWorkcellProtocol.deck_layout),
                selectinload(DBRoboticWorkcellProtocol.run_executions),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_protocols(self, limit: int = 50) -> List[DBRoboticWorkcellProtocol]:
        stmt = (
            select(DBRoboticWorkcellProtocol)
            .options(
                selectinload(DBRoboticWorkcellProtocol.deck_layout),
                selectinload(DBRoboticWorkcellProtocol.run_executions),
            )
            .order_by(desc(DBRoboticWorkcellProtocol.created_at))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
