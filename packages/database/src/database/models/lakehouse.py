"""
SQLAlchemy models for Scientific Multimodal Data Lakehouse (Phase 52).
Stores table metadata, partitions, and semantic hybrid query execution logs.
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship

from database.connection import Base


class DBDataLakeTable(Base):
    """Represents a registered multimodal scientific dataset / table in the lakehouse."""
    __tablename__ = "datalake_tables"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    modality = Column(String(50), nullable=False, index=True)  # GENOMIC, PROTEOMIC, IMAGING, TABULAR, LITERATURE
    storage_format = Column(String(50), nullable=False)  # PARQUET, FASTA, PDB, DICOM, ARROW, JSONL
    schema_definition = Column(JSON, nullable=False, default=dict)  # Column definitions, types, dimensions
    total_records = Column(Integer, default=0)
    size_bytes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    partitions = relationship(
        "DBDataLakePartition",
        back_populates="table",
        cascade="all, delete-orphan",
        order_by="DBDataLakePartition.created_at.desc()",
    )


class DBDataLakePartition(Base):
    """Represents a physical storage partition of a scientific lakehouse table."""
    __tablename__ = "datalake_partitions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    table_id = Column(String(36), ForeignKey("datalake_tables.id", ondelete="CASCADE"), nullable=False, index=True)
    partition_key = Column(String(255), nullable=False)  # e.g., study_id=GSE1234/organism=homo_sapiens
    record_count = Column(Integer, nullable=False, default=0)
    size_bytes = Column(Integer, nullable=False, default=0)
    storage_path = Column(String(500), nullable=False)
    vector_indexed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    table = relationship("DBDataLakeTable", back_populates="partitions")


class DBSemanticLakeQuery(Base):
    """Logs executed semantic and hybrid vector-SQL queries against the lakehouse."""
    __tablename__ = "semantic_lake_queries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    query_text = Column(Text, nullable=False)
    target_tables = Column(JSON, nullable=False, default=list)  # List of table names queried
    sql_predicate = Column(Text, nullable=True)  # Structured SQL WHERE pushdown filter
    vector_similarity_threshold = Column(Float, default=0.75)
    matched_records_count = Column(Integer, default=0)
    execution_time_ms = Column(Float, default=0.0)
    results_preview = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
