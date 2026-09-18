"""Laboratory Robotics Automation & Self-Driving Workcell Protocol Models."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from database.connection import Base


class DBRoboticWorkcellProtocol(Base):
    __tablename__ = "robotic_workcell_protocols"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    protocol_name = Column(String(255), nullable=False)
    robot_platform = Column(String(64), default="OPENTRONS_OT2")
    target_liquid_class = Column(String(64), default="WATER_FREE")
    total_aspirations_count = Column(Integer, default=96)
    total_dispenses_count = Column(Integer, default=96)
    compiled_python_script = Column(Text, default="")
    execution_status = Column(String(32), default="COMPILED")
    protocol_metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    deck_layout = relationship("DBDeckLayoutInstruction", back_populates="protocol", cascade="all, delete-orphan")
    run_executions = relationship("DBAutomatedRunExecution", back_populates="protocol", cascade="all, delete-orphan")


class DBDeckLayoutInstruction(Base):
    __tablename__ = "deck_layout_instructions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    protocol_id = Column(String(36), ForeignKey("robotic_workcell_protocols.id", ondelete="CASCADE"), nullable=False)
    slot_number = Column(Integer, default=1)
    labware_name = Column(String(128), nullable=False)
    labware_type = Column(String(64), default="PLATE")
    initial_volume_ul = Column(Float, default=200.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    protocol = relationship("DBRoboticWorkcellProtocol", back_populates="deck_layout")


class DBAutomatedRunExecution(Base):
    __tablename__ = "automated_run_executions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    protocol_id = Column(String(36), ForeignKey("robotic_workcell_protocols.id", ondelete="CASCADE"), nullable=False)
    run_id_hash = Column(String(64), nullable=False)
    robot_serial_number = Column(String(64), default="OT2-PROD-WORKCELL-01")
    total_run_duration_seconds = Column(Float, default=345.0)
    tips_consumed = Column(Integer, default=96)
    aspiration_accuracy_pct = Column(Float, default=99.4)
    collision_check_passed = Column(Boolean, default=True)
    run_log_text = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    protocol = relationship("DBRoboticWorkcellProtocol", back_populates="run_executions")
