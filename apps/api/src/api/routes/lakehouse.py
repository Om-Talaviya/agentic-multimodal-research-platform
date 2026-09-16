"""
REST API routes for Scientific Multimodal Data Lakehouse (Phase 52).
Provides dataset registration, partition management, and hybrid semantic query endpoints.
"""
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session
from database.repositories.lakehouse_repo import DataLakeRepository
from research.lakehouse.lakehouse_engine import ScientificLakehouseEngine

router = APIRouter(prefix="/lakehouse", tags=["Scientific Data Lakehouse"])
engine = ScientificLakehouseEngine()


# ---------------------------------------------------------------------------
# Pydantic Request & Response Schemas
# ---------------------------------------------------------------------------

class TableCreateRequest(BaseModel):
    name: str = Field(..., example="pan_cancer_tcga_rnaseq")
    modality: str = Field(..., example="GENOMIC")
    storage_format: str = Field(..., example="PARQUET")
    description: Optional[str] = Field(None, example="TCGA Pan-Cancer single-cell and bulk RNA-seq count matrix")
    schema_definition: Optional[Dict[str, Any]] = Field(default_factory=dict)
    total_records: int = Field(0, example=150000)
    size_bytes: int = Field(0, example=1073741824)


class PartitionCreateRequest(BaseModel):
    partition_key: str = Field(..., example="cohort=TCGA-LUAD/year=2026")
    record_count: int = Field(..., example=25000)
    size_bytes: int = Field(..., example=157286400)
    storage_path: str = Field(..., example="s3://lakehouse/genomics/tcga_luad.parquet")
    vector_indexed: bool = Field(True, example=True)


class SemanticQueryRequest(BaseModel):
    query_text: str = Field(..., example="Identify kinase inhibitor resistance mutations in EGFR exon 20 insertions")
    target_tables: List[str] = Field(..., example=["pan_cancer_tcga_rnaseq", "pdb_kinase_structures"])
    sql_predicate: Optional[str] = Field(None, example="p_value < 0.001 AND fold_change > 2.0")
    vector_similarity_threshold: float = Field(0.75, ge=0.0, le=1.0)
    limit: int = Field(10, ge=1, le=100)


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------

@router.post("/tables", status_code=status.HTTP_201_CREATED)
async def create_table(
    req: TableCreateRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Register a new multimodal scientific table with validated schema."""
    repo = DataLakeRepository(db)
    existing = await repo.get_table_by_name(req.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Table '{req.name}' already exists in the lakehouse.",
        )

    validated_schema = engine.validate_schema(
        modality=req.modality,
        storage_format=req.storage_format,
        schema_def=req.schema_definition or {},
    )

    table = await repo.create_table(
        name=req.name,
        modality=req.modality.upper(),
        storage_format=req.storage_format.upper(),
        schema_definition=validated_schema,
        description=req.description,
        total_records=req.total_records,
        size_bytes=req.size_bytes,
    )
    return table


@router.get("/tables")
async def list_tables(
    modality: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session),
):
    """List all registered scientific tables."""
    repo = DataLakeRepository(db)
    tables = await repo.list_tables(modality=modality, limit=limit)
    response_list = []
    for t in tables:
        partitions = await repo.list_partitions(t.id)
        response_list.append({
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "modality": t.modality,
            "storage_format": t.storage_format,
            "schema_definition": t.schema_definition,
            "total_records": t.total_records,
            "size_bytes": t.size_bytes,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
            "partitions": [
                {
                    "id": p.id,
                    "table_id": p.table_id,
                    "partition_key": p.partition_key,
                    "record_count": p.record_count,
                    "size_bytes": p.size_bytes,
                    "storage_path": p.storage_path,
                    "vector_indexed": p.vector_indexed,
                }
                for p in partitions
            ]
        })
    return response_list


@router.get("/tables/{table_id}")
async def get_table(
    table_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get table details and partitions."""
    repo = DataLakeRepository(db)
    table = await repo.get_table(table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Lakehouse table not found.")
    partitions = await repo.list_partitions(table_id)
    return {
        "id": table.id,
        "name": table.name,
        "description": table.description,
        "modality": table.modality,
        "storage_format": table.storage_format,
        "schema_definition": table.schema_definition,
        "total_records": table.total_records,
        "size_bytes": table.size_bytes,
        "created_at": table.created_at.isoformat() if table.created_at else None,
        "updated_at": table.updated_at.isoformat() if table.updated_at else None,
        "partitions": [
            {
                "id": p.id,
                "table_id": p.table_id,
                "partition_key": p.partition_key,
                "record_count": p.record_count,
                "size_bytes": p.size_bytes,
                "storage_path": p.storage_path,
                "vector_indexed": p.vector_indexed,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in partitions
        ]
    }


@router.delete("/tables/{table_id}", status_code=status.HTTP_200_OK)
async def delete_table(
    table_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Delete a table from the lakehouse."""
    repo = DataLakeRepository(db)
    deleted = await repo.delete_table(table_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Lakehouse table not found.")
    return {"status": "success", "message": f"Table {table_id} deleted."}


@router.post("/tables/{table_id}/partitions", status_code=status.HTTP_201_CREATED)
async def add_partition(
    table_id: str,
    req: PartitionCreateRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Add a partition to an existing table."""
    repo = DataLakeRepository(db)
    table = await repo.get_table(table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Lakehouse table not found.")

    partition = await repo.add_partition(
        table_id=table_id,
        partition_key=req.partition_key,
        record_count=req.record_count,
        size_bytes=req.size_bytes,
        storage_path=req.storage_path,
        vector_indexed=req.vector_indexed,
    )
    return partition


@router.post("/query", status_code=status.HTTP_200_OK)
async def execute_semantic_query(
    req: SemanticQueryRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """Execute hybrid Vector + SQL Semantic Query against the Lakehouse."""
    repo = DataLakeRepository(db)
    
    # 1. Execute query via Lakehouse engine
    query_result = engine.execute_hybrid_query(
        query_text=req.query_text,
        target_tables=req.target_tables,
        sql_predicate=req.sql_predicate,
        vector_threshold=req.vector_similarity_threshold,
        limit=req.limit,
    )

    # 2. Persist query execution audit
    record = await repo.record_query(
        query_text=req.query_text,
        target_tables=req.target_tables,
        sql_predicate=req.sql_predicate,
        vector_similarity_threshold=req.vector_similarity_threshold,
        matched_records_count=query_result["matched_records_count"],
        execution_time_ms=query_result["execution_time_ms"],
        results_preview=query_result["results_preview"],
    )

    return {
        "query_id": record.id,
        "query_text": req.query_text,
        "matched_records_count": query_result["matched_records_count"],
        "execution_time_ms": query_result["execution_time_ms"],
        "results": query_result["results_preview"],
    }


@router.get("/queries")
async def list_queries(
    limit: int = 30,
    db: AsyncSession = Depends(get_db_session),
):
    """List historical queries."""
    repo = DataLakeRepository(db)
    return await repo.list_queries(limit=limit)


@router.get("/metrics")
async def get_metrics(
    db: AsyncSession = Depends(get_db_session),
):
    """Get lakehouse aggregate storage & record metrics."""
    repo = DataLakeRepository(db)
    return await repo.get_metrics()
