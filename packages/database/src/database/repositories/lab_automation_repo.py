"""Autonomous Laboratory Automation & Robotic Protocol Repository (Phase 37)."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.lab_automation import (
    DBLabwareSlot,
    DBLiquidTransferStep,
    DBRoboticExecutionTrace,
    DBRoboticProtocol,
)
from shared.logging import get_logger

logger = get_logger(__name__)


class LabAutomationRepository:
    """Async repository for robotic protocols, deck slot layouts, pipetting transfer steps, and execution traces."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_protocol(
        self,
        user_id: uuid.UUID | str,
        protocol_name: str,
        robot_platform: str = "Opentrons_OT2",
        assay_type: str = "CRISPR_LNP_Formulation",
        deck_layout_json: Optional[Dict[str, Any]] = None,
        total_runtime_minutes: float = 18.5,
        liquid_waste_volume_ml: float = 2.4,
        validation_status: str = "valid",
        protocol_python_code: str = "",
        autoprotocol_json: Optional[Dict[str, Any]] = None,
        workspace_id: Optional[uuid.UUID | str] = None,
        project_id: Optional[uuid.UUID | str] = None,
    ) -> DBRoboticProtocol:
        """Create and persist a new robotic protocol specification."""
        protocol = DBRoboticProtocol(
            id=uuid.uuid4(),
            user_id=user_id,
            workspace_id=workspace_id,
            project_id=project_id,
            protocol_name=protocol_name,
            robot_platform=robot_platform,
            assay_type=assay_type,
            deck_layout_json=deck_layout_json or {},
            total_runtime_minutes=total_runtime_minutes,
            liquid_waste_volume_ml=liquid_waste_volume_ml,
            validation_status=validation_status,
            protocol_python_code=protocol_python_code,
            autoprotocol_json=autoprotocol_json or {},
        )
        self._session.add(protocol)
        await self._session.flush()
        logger.info(
            "robotic_protocol_created",
            protocol_id=str(protocol.id),
            name=protocol_name,
            platform=robot_platform,
        )
        return protocol

    async def get_protocol(self, protocol_id: uuid.UUID | str) -> Optional[DBRoboticProtocol]:
        """Fetch a robotic protocol by ID with all deck slots, transfer steps, and execution traces."""
        stmt = (
            select(DBRoboticProtocol)
            .where(DBRoboticProtocol.id == protocol_id)
            .options(
                selectinload(DBRoboticProtocol.deck_slots),
                selectinload(DBRoboticProtocol.transfer_steps),
                selectinload(DBRoboticProtocol.execution_traces),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalars().first()

    async def list_protocols(
        self,
        user_id: Optional[uuid.UUID | str] = None,
        workspace_id: Optional[uuid.UUID | str] = None,
        project_id: Optional[uuid.UUID | str] = None,
        robot_platform: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[DBRoboticProtocol]:
        """List robotic protocols filtered by user, workspace, project, or platform."""
        stmt = (
            select(DBRoboticProtocol)
            .options(
                selectinload(DBRoboticProtocol.deck_slots),
                selectinload(DBRoboticProtocol.transfer_steps),
                selectinload(DBRoboticProtocol.execution_traces),
            )
            .order_by(desc(DBRoboticProtocol.created_at))
            .limit(limit)
            .offset(offset)
        )

        if project_id:
            stmt = stmt.where(DBRoboticProtocol.project_id == project_id)
        elif workspace_id:
            stmt = stmt.where(DBRoboticProtocol.workspace_id == workspace_id)
        elif user_id:
            stmt = stmt.where(DBRoboticProtocol.user_id == user_id)

        if robot_platform:
            stmt = stmt.where(DBRoboticProtocol.robot_platform == robot_platform)

        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def add_deck_slot(
        self,
        protocol_id: uuid.UUID | str,
        slot_number: int,
        labware_type: str,
        reagent_name: Optional[str] = None,
        initial_volume_ul: float = 0.0,
        current_volume_ul: float = 0.0,
    ) -> DBLabwareSlot:
        """Add a labware deck position allocation to a protocol."""
        slot = DBLabwareSlot(
            id=uuid.uuid4(),
            protocol_id=protocol_id,
            slot_number=slot_number,
            labware_type=labware_type,
            reagent_name=reagent_name,
            initial_volume_ul=initial_volume_ul,
            current_volume_ul=current_volume_ul if current_volume_ul > 0 else initial_volume_ul,
        )
        self._session.add(slot)
        await self._session.flush()
        return slot

    async def add_deck_slots(
        self,
        protocol_id: uuid.UUID | str,
        slots_data: List[Dict[str, Any]],
    ) -> List[DBLabwareSlot]:
        """Batch add labware deck positions to a protocol."""
        created_slots = []
        for s in slots_data:
            init_vol = float(s.get("initial_volume_ul", 0.0))
            curr_vol = float(s.get("current_volume_ul", init_vol))
            slot = DBLabwareSlot(
                id=uuid.uuid4(),
                protocol_id=protocol_id,
                slot_number=int(s["slot_number"]),
                labware_type=str(s["labware_type"]),
                reagent_name=s.get("reagent_name"),
                initial_volume_ul=init_vol,
                current_volume_ul=curr_vol,
            )
            self._session.add(slot)
            created_slots.append(slot)
        await self._session.flush()
        return created_slots

    async def add_transfer_step(
        self,
        protocol_id: uuid.UUID | str,
        step_index: int,
        source_slot: int,
        source_well: str,
        target_slot: int,
        target_well: str,
        volume_ul: float,
        pipette_name: str = "p300_single_gen2",
        transfer_type: str = "transfer",
        liquid_class: str = "aqueous",
    ) -> DBLiquidTransferStep:
        """Add an atomic liquid transfer step to a protocol."""
        step = DBLiquidTransferStep(
            id=uuid.uuid4(),
            protocol_id=protocol_id,
            step_index=step_index,
            source_slot=source_slot,
            source_well=source_well,
            target_slot=target_slot,
            target_well=target_well,
            volume_ul=volume_ul,
            pipette_name=pipette_name,
            transfer_type=transfer_type,
            liquid_class=liquid_class,
        )
        self._session.add(step)
        await self._session.flush()
        return step

    async def add_transfer_steps(
        self,
        protocol_id: uuid.UUID | str,
        steps_data: List[Dict[str, Any]],
    ) -> List[DBLiquidTransferStep]:
        """Batch add transfer steps to a protocol."""
        created_steps = []
        for st in steps_data:
            step = DBLiquidTransferStep(
                id=uuid.uuid4(),
                protocol_id=protocol_id,
                step_index=int(st.get("step_index", len(created_steps) + 1)),
                source_slot=int(st["source_slot"]),
                source_well=str(st["source_well"]),
                target_slot=int(st["target_slot"]),
                target_well=str(st["target_well"]),
                volume_ul=float(st["volume_ul"]),
                pipette_name=str(st.get("pipette_name", "p300_single_gen2")),
                transfer_type=str(st.get("transfer_type", "transfer")),
                liquid_class=str(st.get("liquid_class", "aqueous")),
            )
            self._session.add(step)
            created_steps.append(step)
        await self._session.flush()
        return created_steps

    async def record_execution_trace(
        self,
        protocol_id: uuid.UUID | str,
        step_count: int,
        simulated_runtime_sec: float,
        estimated_tip_count: int,
        tip_waste_pct: float,
        collision_warnings: Optional[List[Dict[str, Any]]] = None,
        simulation_log: Optional[List[Dict[str, Any]]] = None,
    ) -> DBRoboticExecutionTrace:
        """Record simulation results and collision analysis for a protocol."""
        trace = DBRoboticExecutionTrace(
            id=uuid.uuid4(),
            protocol_id=protocol_id,
            step_count=step_count,
            simulated_runtime_sec=simulated_runtime_sec,
            estimated_tip_count=estimated_tip_count,
            tip_waste_pct=tip_waste_pct,
            collision_warnings=collision_warnings or [],
            simulation_log=simulation_log or [],
        )
        self._session.add(trace)
        await self._session.flush()
        logger.info(
            "robotic_simulation_recorded",
            protocol_id=str(protocol_id),
            runtime_sec=simulated_runtime_sec,
            tips=estimated_tip_count,
            collisions=len(collision_warnings or []),
        )
        return trace
