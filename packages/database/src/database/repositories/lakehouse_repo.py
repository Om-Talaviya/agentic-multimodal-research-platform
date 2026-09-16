"""
Repository for Scientific Multimodal Data Lakehouse (Phase 52).
Handles CRUD for tables, partitions, and semantic query execution logs.
"""
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.lakehouse import (
    DBDataLakeTable,
    DBDataLakePartition,
    DBSemanticLakeQuery,
)


class DataLakeRepository:
    """Repository handling persistence for Data Lakehouse tables, partitions, and query logs."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_table(
        self,
        name: str,
        modality: str,
        storage_format: str,
        schema_definition: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        total_records: int = 0,
        size_bytes: int = 0,
    ) -> DBDataLakeTable:
        """Register a new multimodal table in the lakehouse."""
        table = DBDataLakeTable(
            name=name,
            modality=modality,
            storage_format=storage_format,
            schema_definition=schema_definition or {},
            description=description,
            total_records=total_records,
            size_bytes=size_bytes,
        )
        self.session.add(table)
        await self.session.commit()
        await self.session.refresh(table)
        return table

    async def get_table(self, table_id: str) -> Optional[DBDataLakeTable]:
        """Fetch table with all partitions loaded."""
        stmt = (
            select(DBDataLakeTable)
            .where(DBDataLakeTable.id == table_id)
            .options(selectinload(DBDataLakeTable.partitions))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_table_by_name(self, name: str) -> Optional[DBDataLakeTable]:
        """Fetch table by unique name."""
        stmt = (
            select(DBDataLakeTable)
            .where(DBDataLakeTable.name == name)
            .options(selectinload(DBDataLakeTable.partitions))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_tables(self, modality: Optional[str] = None, limit: int = 50) -> List[DBDataLakeTable]:
        """List all tables with optional modality filtering."""
        stmt = select(DBDataLakeTable).options(selectinload(DBDataLakeTable.partitions))
        if modality:
            stmt = stmt.where(DBDataLakeTable.modality == modality)
        stmt = stmt.order_by(DBDataLakeTable.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_table(self, table_id: str) -> bool:
        """Delete table and cascade partitions."""
        table = await self.get_table(table_id)
        if not table:
            return False
        await self.session.delete(table)
        await self.session.commit()
        return True

    async def add_partition(
        self,
        table_id: str,
        partition_key: str,
        record_count: int,
        size_bytes: int,
        storage_path: str,
        vector_indexed: bool = False,
    ) -> DBDataLakePartition:
        """Register a new storage partition and increment table totals."""
        partition = DBDataLakePartition(
            table_id=table_id,
            partition_key=partition_key,
            record_count=record_count,
            size_bytes=size_bytes,
            storage_path=storage_path,
            vector_indexed=vector_indexed,
        )
        self.session.add(partition)

        # Update table aggregate metrics
        table = await self.get_table(table_id)
        if table:
            table.total_records += record_count
            table.size_bytes += size_bytes

        await self.session.commit()
        await self.session.refresh(partition)
        return partition

    async def list_partitions(self, table_id: str) -> List[DBDataLakePartition]:
        """List all partitions for a given table."""
        stmt = (
            select(DBDataLakePartition)
            .where(DBDataLakePartition.table_id == table_id)
            .order_by(DBDataLakePartition.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def record_query(
        self,
        query_text: str,
        target_tables: List[str],
        sql_predicate: Optional[str] = None,
        vector_similarity_threshold: float = 0.75,
        matched_records_count: int = 0,
        execution_time_ms: float = 0.0,
        results_preview: Optional[List[Dict[str, Any]]] = None,
    ) -> DBSemanticLakeQuery:
        """Log a hybrid semantic Lakehouse query execution."""
        record = DBSemanticLakeQuery(
            query_text=query_text,
            target_tables=target_tables,
            sql_predicate=sql_predicate,
            vector_similarity_threshold=vector_similarity_threshold,
            matched_records_count=matched_records_count,
            execution_time_ms=execution_time_ms,
            results_preview=results_preview or [],
        )
        self.session.add(record)
        await self.session.commit()
        await self.session.refresh(record)
        return record

    async def list_queries(self, limit: int = 30) -> List[DBSemanticLakeQuery]:
        """List historical lakehouse queries."""
        stmt = select(DBSemanticLakeQuery).order_by(DBSemanticLakeQuery.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_metrics(self) -> Dict[str, Any]:
        """Compute lakehouse aggregate statistics."""
        t_res = await self.session.execute(select(func.count(DBDataLakeTable.id)))
        total_tables = t_res.scalar() or 0

        p_res = await self.session.execute(select(func.count(DBDataLakePartition.id)))
        total_partitions = p_res.scalar() or 0

        rec_res = await self.session.execute(select(func.sum(DBDataLakeTable.total_records)))
        total_records = rec_res.scalar() or 0

        sz_res = await self.session.execute(select(func.sum(DBDataLakeTable.size_bytes)))
        total_bytes = sz_res.scalar() or 0

        q_res = await self.session.execute(select(func.count(DBSemanticLakeQuery.id)))
        total_queries = q_res.scalar() or 0

        return {
            "total_tables": total_tables,
            "total_partitions": total_partitions,
            "total_records": int(total_records),
            "total_bytes": int(total_bytes),
            "total_queries": total_queries,
        }
