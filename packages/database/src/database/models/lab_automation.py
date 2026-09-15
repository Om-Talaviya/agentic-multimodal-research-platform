"""Autonomous Laboratory Automation & Robotic Liquid Handling Database Models (Phase 37)."""

import uuid
from datetime import UTC, datetime
from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from database.connection import Base
from database.models.memory import GUID, JSONType


def utc_now() -> datetime:
    return datetime.now(UTC)


class DBRoboticProtocol(Base):
    """Robotic liquid-handling protocol specification for automated workstations."""

    __tablename__ = "robotic_protocols"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace_id = Column(GUID(), ForeignKey("workspaces.id", ondelete="SET NULL"), nullable=True, index=True)
    project_id = Column(GUID(), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)

    protocol_name = Column(String(300), nullable=False)
    robot_platform = Column(String(100), nullable=False, default="Opentrons_OT2")  # Opentrons_OT2, Opentrons_Flex, PyLabRobot_Universal, Tecan_Fluent, Hamilton_STAR
    assay_type = Column(String(100), nullable=False, default="CRISPR_LNP_Formulation")  # CRISPR_LNP_Formulation, qPCR_Assay, ELISA_Screening, Serial_Dilution, PCR_MasterMix
    deck_layout_json = Column(JSONType, nullable=False, default=dict)
    total_runtime_minutes = Column(Float, nullable=False, default=18.5)
    liquid_waste_volume_ml = Column(Float, nullable=False, default=2.4)
    validation_status = Column(String(50), nullable=False, default="valid")  # valid, syntax_error, collision_detected, tip_exhaustion_warning

    protocol_python_code = Column(Text, nullable=False)
    autoprotocol_json = Column(JSONType, nullable=False, default=dict)

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    deck_slots = relationship(
        "DBLabwareSlot",
        back_populates="protocol",
        cascade="all, delete-orphan",
        order_by="DBLabwareSlot.slot_number",
    )
    transfer_steps = relationship(
        "DBLiquidTransferStep",
        back_populates="protocol",
        cascade="all, delete-orphan",
        order_by="DBLiquidTransferStep.step_index",
    )
    execution_traces = relationship(
        "DBRoboticExecutionTrace",
        back_populates="protocol",
        cascade="all, delete-orphan",
    )


class DBLabwareSlot(Base):
    """Deck position allocation on robotic workstation."""

    __tablename__ = "robotic_deck_slots"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    protocol_id = Column(GUID(), ForeignKey("robotic_protocols.id", ondelete="CASCADE"), nullable=False, index=True)

    slot_number = Column(Integer, nullable=False)  # 1 to 12
    labware_type = Column(String(150), nullable=False)  # e.g., corning_96_wellplate_360ul_flat, opentrons_96_tiprack_300ul
    reagent_name = Column(String(200), nullable=True)
    initial_volume_ul = Column(Float, nullable=False, default=0.0)
    current_volume_ul = Column(Float, nullable=False, default=0.0)

    # Relationships
    protocol = relationship("DBRoboticProtocol", back_populates="deck_slots")


class DBLiquidTransferStep(Base):
    """Atomic pipetting operation within robotic protocol."""

    __tablename__ = "robotic_transfer_steps"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    protocol_id = Column(GUID(), ForeignKey("robotic_protocols.id", ondelete="CASCADE"), nullable=False, index=True)

    step_index = Column(Integer, nullable=False)
    source_slot = Column(Integer, nullable=False)
    source_well = Column(String(20), nullable=False)  # e.g., "A1"
    target_slot = Column(Integer, nullable=False)
    target_well = Column(String(20), nullable=False)  # e.g., "B2"
    volume_ul = Column(Float, nullable=False)
    pipette_name = Column(String(100), nullable=False, default="p300_single_gen2")
    transfer_type = Column(String(50), nullable=False, default="transfer")  # transfer, aspirate, dispense, mix, blowout
    liquid_class = Column(String(50), nullable=False, default="aqueous")  # aqueous, viscous_glycerol, volatile_ethanol

    # Relationships
    protocol = relationship("DBRoboticProtocol", back_populates="transfer_steps")


class DBRoboticExecutionTrace(Base):
    """Virtual simulation trace and collision assessment for robotic protocol."""

    __tablename__ = "robotic_execution_traces"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    protocol_id = Column(GUID(), ForeignKey("robotic_protocols.id", ondelete="CASCADE"), nullable=False, index=True)

    step_count = Column(Integer, nullable=False, default=0)
    simulated_runtime_sec = Column(Float, nullable=False, default=0.0)
    estimated_tip_count = Column(Integer, nullable=False, default=0)
    tip_waste_pct = Column(Float, nullable=False, default=0.0)
    collision_warnings = Column(JSONType, nullable=False, default=list)
    simulation_log = Column(JSONType, nullable=False, default=list)

    executed_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    protocol = relationship("DBRoboticProtocol", back_populates="execution_traces")
