import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from database.connection import Base

class DBFlowCytometryExperiment(Base):
    __tablename__ = "flow_cytometry_experiments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_name = Column(String(255), nullable=False)
    sample_id = Column(String(100), nullable=False)
    cell_type = Column(String(100), nullable=False, default="PBMC")  # PBMC, Jurkat, CAR-T, Splenocytes
    panel_markers = Column(JSON, default=list)  # ["CD3-FITC", "CD4-PE", "CD8-APC", "Live/Dead-eFluor780"]
    fcs_file_path = Column(String(500), nullable=True)
    total_event_count = Column(Integer, nullable=False, default=50000)
    properties = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    gates = relationship("DBBivariateGatingHierarchy", back_populates="experiment", cascade="all, delete-orphan")
    z_prime_metrics = relationship("DBAssayZPrimeMetric", back_populates="experiment", cascade="all, delete-orphan")

class DBBivariateGatingHierarchy(Base):
    __tablename__ = "flow_cytometry_gates"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_id = Column(String(36), ForeignKey("flow_cytometry_experiments.id", ondelete="CASCADE"), nullable=False)
    gate_name = Column(String(100), nullable=False)  # Lymphocytes, Singlets, Live Cells, CD3+CD8+
    parent_gate_id = Column(String(36), nullable=True)
    x_channel = Column(String(50), nullable=False)  # FSC-A, FSC-H, CD3-FITC, CD4-PE
    y_channel = Column(String(50), nullable=False)  # SSC-A, FSC-W, CD8-APC, Live/Dead
    polygon_vertices_json = Column(JSON, default=list)  # [[x1, y1], [x2, y2], ...]
    gated_event_count = Column(Integer, nullable=False)
    population_pct_of_parent = Column(Float, nullable=False)  # % of parent gate
    population_pct_of_total = Column(Float, nullable=False)  # % of total events
    created_at = Column(DateTime, default=datetime.utcnow)

    experiment = relationship("DBFlowCytometryExperiment", back_populates="gates")

class DBAssayZPrimeMetric(Base):
    __tablename__ = "flow_cytometry_zprime_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_id = Column(String(36), ForeignKey("flow_cytometry_experiments.id", ondelete="CASCADE"), nullable=False)
    plate_id = Column(String(100), nullable=False)
    positive_control_mean = Column(Float, nullable=False)
    positive_control_sd = Column(Float, nullable=False)
    negative_control_mean = Column(Float, nullable=False)
    negative_control_sd = Column(Float, nullable=False)
    z_prime_factor = Column(Float, nullable=False)  # 1 - (3*(SD_pos + SD_neg) / |Mean_pos - Mean_neg|)
    assay_quality_status = Column(String(50), nullable=False, default="EXCELLENT")  # EXCELLENT, ACCEPTABLE, UNACCEPTABLE
    signal_to_background = Column(Float, nullable=False, default=12.5)
    created_at = Column(DateTime, default=datetime.utcnow)

    experiment = relationship("DBFlowCytometryExperiment", back_populates="z_prime_metrics")
