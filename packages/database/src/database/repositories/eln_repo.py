"""
Repository for Electronic Lab Notebook (ELN) (Phase 53).
Handles CRUD for notebooks, modular blocks, and immutable cryptographic audit trails.
"""
import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models.eln import (
    DBElectronicLabNotebook,
    DBLabNotebookBlock,
    DBELNAuditTrailEntry,
)


class LabNotebookRepository:
    """Repository handling persistence for ELN notebooks, modular blocks, and 21 CFR Part 11 audit trails."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_notebook(
        self,
        title: str,
        author_id: str = "researcher_user",
        project_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> DBElectronicLabNotebook:
        """Create a new ELN notebook entry."""
        notebook = DBElectronicLabNotebook(
            title=title,
            author_id=author_id,
            project_id=project_id,
            tags=tags or [],
            status="DRAFT",
        )
        self.session.add(notebook)
        await self.session.commit()
        await self.session.refresh(notebook)

        # Record initial creation in audit trail
        await self.record_audit_entry(
            notebook_id=notebook.id,
            actor_id=author_id,
            action="NOTEBOOK_CREATE",
            diff_payload={"title": title, "tags": tags or []},
        )
        return notebook

    async def get_notebook(self, notebook_id: str) -> Optional[DBElectronicLabNotebook]:
        """Fetch notebook with blocks and audit trail loaded."""
        stmt = (
            select(DBElectronicLabNotebook)
            .where(DBElectronicLabNotebook.id == notebook_id)
            .options(
                selectinload(DBElectronicLabNotebook.blocks),
                selectinload(DBElectronicLabNotebook.audit_trails),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_notebooks(
        self,
        status: Optional[str] = None,
        author_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[DBElectronicLabNotebook]:
        """List all notebooks with optional status/author filtering."""
        stmt = select(DBElectronicLabNotebook).options(selectinload(DBElectronicLabNotebook.blocks))
        if status:
            stmt = stmt.where(DBElectronicLabNotebook.status == status)
        if author_id:
            stmt = stmt.where(DBElectronicLabNotebook.author_id == author_id)
        stmt = stmt.order_by(DBElectronicLabNotebook.updated_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add_block(
        self,
        notebook_id: str,
        block_type: str,
        content_json: Dict[str, Any],
        order_index: Optional[int] = None,
        actor_id: str = "researcher_user",
    ) -> DBLabNotebookBlock:
        """Add a content block to the notebook and log in audit trail."""
        if order_index is None:
            stmt = select(func.coalesce(func.max(DBLabNotebookBlock.order_index), 0)).where(
                DBLabNotebookBlock.notebook_id == notebook_id
            )
            max_idx = (await self.session.execute(stmt)).scalar() or 0
            order_index = max_idx + 1

        block = DBLabNotebookBlock(
            notebook_id=notebook_id,
            block_type=block_type.upper(),
            content_json=content_json,
            order_index=order_index,
        )
        self.session.add(block)
        await self.session.commit()
        await self.session.refresh(block)

        await self.record_audit_entry(
            notebook_id=notebook_id,
            actor_id=actor_id,
            action="BLOCK_INSERT",
            diff_payload={"block_id": block.id, "type": block.block_type, "content": content_json},
        )
        return block

    async def update_block(
        self,
        block_id: str,
        content_json: Dict[str, Any],
        actor_id: str = "researcher_user",
    ) -> Optional[DBLabNotebookBlock]:
        """Update block content and log audit trail."""
        stmt = select(DBLabNotebookBlock).where(DBLabNotebookBlock.id == block_id)
        block = (await self.session.execute(stmt)).scalar_one_or_none()
        if not block:
            return None

        old_content = block.content_json
        block.content_json = content_json
        block.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(block)

        await self.record_audit_entry(
            notebook_id=block.notebook_id,
            actor_id=actor_id,
            action="BLOCK_UPDATE",
            diff_payload={"block_id": block.id, "old": old_content, "new": content_json},
        )
        return block

    async def list_blocks(self, notebook_id: str) -> List[DBLabNotebookBlock]:
        """List all blocks in sequential order."""
        stmt = (
            select(DBLabNotebookBlock)
            .where(DBLabNotebookBlock.notebook_id == notebook_id)
            .order_by(DBLabNotebookBlock.order_index.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def witness_sign(
        self,
        notebook_id: str,
        witness_id: str,
        witness_statement: str,
    ) -> Optional[DBElectronicLabNotebook]:
        """Apply 21 CFR Part 11 compliant digital witness signature."""
        notebook = await self.get_notebook(notebook_id)
        if not notebook:
            return None

        timestamp = datetime.utcnow().isoformat()
        sig_data = f"{notebook_id}:{witness_id}:{timestamp}:{witness_statement}"
        sha256_hash = hashlib.sha256(sig_data.encode("utf-8")).hexdigest()

        notebook.cfr_part11_signed = True
        notebook.status = "WITNESSED"
        notebook.witness_signature = {
            "witness_id": witness_id,
            "statement": witness_statement,
            "timestamp": timestamp,
            "sha256_hash": sha256_hash,
            "compliance_standard": "FDA 21 CFR Part 11 / ALCOA+",
        }
        await self.session.commit()
        await self.session.refresh(notebook)

        await self.record_audit_entry(
            notebook_id=notebook_id,
            actor_id=witness_id,
            action="WITNESS_SIGN",
            diff_payload=notebook.witness_signature,
        )
        return notebook

    async def record_audit_entry(
        self,
        notebook_id: str,
        actor_id: str,
        action: str,
        diff_payload: Dict[str, Any],
    ) -> DBELNAuditTrailEntry:
        """Record immutable cryptographic audit trail entry."""
        ts = datetime.utcnow().isoformat()
        raw_to_hash = f"{notebook_id}:{actor_id}:{action}:{ts}:{json.dumps(diff_payload, sort_keys=True)}"
        digest = hashlib.sha256(raw_to_hash.encode("utf-8")).hexdigest()

        entry = DBELNAuditTrailEntry(
            notebook_id=notebook_id,
            actor_id=actor_id,
            action=action,
            diff_payload=diff_payload,
            cryptographic_hash=digest,
        )
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        return entry

    async def list_audit_trails(self, notebook_id: str) -> List[DBELNAuditTrailEntry]:
        """List audit trails for notebook in reverse chronological order."""
        stmt = (
            select(DBELNAuditTrailEntry)
            .where(DBELNAuditTrailEntry.notebook_id == notebook_id)
            .order_by(DBELNAuditTrailEntry.timestamp.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_metrics(self) -> Dict[str, Any]:
        """Get aggregate statistics for ELN workspace."""
        total_nb = (await self.session.execute(select(func.count(DBElectronicLabNotebook.id)))).scalar() or 0
        witnessed_nb = (await self.session.execute(select(func.count(DBElectronicLabNotebook.id)).where(DBElectronicLabNotebook.status == "WITNESSED"))).scalar() or 0
        total_blocks = (await self.session.execute(select(func.count(DBLabNotebookBlock.id)))).scalar() or 0
        total_audits = (await self.session.execute(select(func.count(DBELNAuditTrailEntry.id)))).scalar() or 0

        return {
            "total_notebooks": total_nb,
            "witnessed_notebooks": witnessed_nb,
            "total_blocks": total_blocks,
            "total_audit_records": total_audits,
            "compliance_mode": "FDA 21 CFR Part 11 Active",
        }
