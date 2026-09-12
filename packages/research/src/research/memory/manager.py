"""Persistent Research Memory Manager for cross-session knowledge consolidation and recall."""

from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_session
from database.models.memory import DBResearchMemory
from database.repositories.memory_repository import MemoryRepository
from research.memory.models import MemoryItem, MemoryRecallResult, MemorySearchRequest, MemoryType
from shared.logging import get_logger

logger = get_logger(__name__)


class ResearchMemoryManager:
    """Orchestrates cross-session conceptual research memory indexing, recall, and consolidation."""

    def __init__(
        self,
        session_or_repo: Optional[Union[AsyncSession, MemoryRepository]] = None,
        retriever: Optional[Any] = None,
        vector_store: Optional[Any] = None,
        embedder: Optional[Any] = None,
    ) -> None:
        if isinstance(session_or_repo, MemoryRepository):
            self.repo: Optional[MemoryRepository] = session_or_repo
        elif session_or_repo is not None:
            self.repo = MemoryRepository(session_or_repo)
        else:
            self.repo = None
        self.retriever = retriever
        self.vector_store = vector_store
        self.embedder = embedder

    async def _execute_with_repo(self, callback):
        """Execute callback with an available repository or a new session."""
        if self.repo is not None:
            return await callback(self.repo)
        async with get_session() as session:
            repo = MemoryRepository(session)
            return await callback(repo)

    async def store_memory(
        self,
        title: str,
        content: str,
        memory_type: Union[MemoryType, str] = MemoryType.FINDING,
        user_id: Optional[Union[UUID, str]] = None,
        job_id: Optional[Union[UUID, str]] = None,
        project_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        confidence: float = 1.0,
        source_type: str = "manual",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryItem:
        """Explicitly store a single conceptual memory item."""
        u_uuid = UUID(str(user_id)) if user_id else uuid4()
        j_uuid = UUID(str(job_id)) if job_id else None
        m_type = memory_type.value if hasattr(memory_type, "value") else str(memory_type)

        db_item = DBResearchMemory(
            id=uuid4(),
            user_id=u_uuid,
            job_id=j_uuid,
            project_id=project_id,
            memory_type=m_type,
            title=title,
            content=content,
            confidence_score=confidence,
            tags=tags or [],
            provenance_json=metadata or {"source": source_type},
            is_pinned=False,
            access_count=0,
        )

        async def _save(repo: MemoryRepository):
            return await repo.create(db_item)

        saved = await self._execute_with_repo(_save)

        return MemoryItem(
            id=str(saved.id),
            user_id=str(saved.user_id) if saved.user_id else None,
            job_id=str(saved.job_id) if saved.job_id else None,
            project_id=saved.project_id,
            memory_type=MemoryType(saved.memory_type) if saved.memory_type in [m.value for m in MemoryType] else MemoryType.FINDING,
            title=saved.title,
            content=saved.content,
            confidence_score=saved.confidence_score,
            confidence=saved.confidence_score,
            tags=saved.tags or [],
            provenance=saved.provenance_json or {},
            source_type=source_type,
            is_pinned=saved.is_pinned,
            access_count=saved.access_count,
            created_at=saved.created_at.isoformat() if saved.created_at else None,
            updated_at=saved.updated_at.isoformat() if saved.updated_at else None,
            metadata=saved.provenance_json or {},
        )

    async def store_memories_from_report(
        self,
        report_data: Union[Dict[str, Any], Any] = None,
        report: Optional[Any] = None,
        user_id: Optional[Union[UUID, str]] = None,
        job_id: Optional[Union[UUID, str]] = None,
        project_id: Optional[str] = None,
        confidence_score: Optional[float] = None,
    ) -> List[MemoryItem]:
        """Extract durable findings, verified claims, and hypotheses from a completed research report."""
        u_uuid = UUID(str(user_id)) if user_id else uuid4()
        j_uuid = UUID(str(job_id)) if job_id else None

        # Harmonize input data
        data: Dict[str, Any] = {}
        if report is not None:
            if hasattr(report, "model_dump"):
                data = report.model_dump()
            elif isinstance(report, dict):
                data = report
            if not j_uuid and getattr(report, "job_id", None):
                j_uuid = UUID(str(report.job_id))
            if confidence_score is None:
                confidence_score = getattr(report, "confidence_score", None)
        elif isinstance(report_data, dict):
            data = report_data
        elif hasattr(report_data, "model_dump"):
            data = report_data.model_dump()

        report_title = data.get("title") or "Research Report"
        domain_tag = data.get("metadata", {}).get("domain", "general") if isinstance(data.get("metadata"), dict) else "general"
        conf = float(confidence_score if confidence_score is not None else data.get("confidence_score", 0.90))

        memories_to_create: List[DBResearchMemory] = []

        # 1. Extract Executive Summary as SUMMARY memory
        exec_sum = data.get("executive_summary") or data.get("summary")
        if exec_sum and len(str(exec_sum).strip()) > 10:
            memories_to_create.append(
                DBResearchMemory(
                    id=uuid4(),
                    user_id=u_uuid,
                    job_id=j_uuid,
                    project_id=project_id,
                    memory_type=MemoryType.SUMMARY.value,
                    title=f"Summary: {report_title[:70]}",
                    content=str(exec_sum).strip(),
                    confidence_score=conf,
                    tags=[domain_tag, "summary"],
                    provenance_json={"report_title": report_title},
                )
            )

        # 2. Extract Methodology as METHODOLOGY memory
        methodology = data.get("methodology")
        if methodology and len(str(methodology).strip()) > 10:
            memories_to_create.append(
                DBResearchMemory(
                    id=uuid4(),
                    user_id=u_uuid,
                    job_id=j_uuid,
                    project_id=project_id,
                    memory_type=MemoryType.METHODOLOGY.value,
                    title=f"Methodology: {report_title[:70]}",
                    content=str(methodology).strip(),
                    confidence_score=conf,
                    tags=[domain_tag, "methodology"],
                    provenance_json={"report_title": report_title},
                )
            )

        # 3. Extract Key Findings as FINDING memories
        raw_findings = data.get("findings") or data.get("key_findings") or []
        for idx, finding in enumerate(raw_findings):
            finding_text = str(finding).strip()
            if not finding_text or len(finding_text) < 10:
                continue
            f_title = finding_text[:80].rstrip(".") + "..." if len(finding_text) > 80 else finding_text
            memories_to_create.append(
                DBResearchMemory(
                    id=uuid4(),
                    user_id=u_uuid,
                    job_id=j_uuid,
                    project_id=project_id,
                    memory_type=MemoryType.FINDING.value,
                    title=f"Finding: {f_title}",
                    content=finding_text,
                    confidence_score=conf,
                    tags=[domain_tag, "finding"],
                    provenance_json={"finding_index": idx, "report_title": report_title},
                )
            )

        # 4. Extract Contradictions as CONTRADICTION memories
        raw_contras = data.get("contradictions") or []
        for c_idx, contra in enumerate(raw_contras):
            c_dict = contra if isinstance(contra, dict) else (contra.model_dump() if hasattr(contra, "model_dump") else {})
            topic = c_dict.get("topic") or c_dict.get("claim_a") or f"Contradiction #{c_idx+1}"
            explanation = c_dict.get("explanation") or f"Conflict: {c_dict.get('claim_a')} vs {c_dict.get('claim_b')}"
            memories_to_create.append(
                DBResearchMemory(
                    id=uuid4(),
                    user_id=u_uuid,
                    job_id=j_uuid,
                    project_id=project_id,
                    memory_type=MemoryType.CONTRADICTION.value,
                    title=f"Contradiction: {str(topic)[:70]}",
                    content=str(explanation),
                    confidence_score=0.85,
                    tags=[domain_tag, "contradiction", str(c_dict.get("severity", "medium"))],
                    provenance_json=c_dict,
                )
            )

        if not memories_to_create:
            logger.info("No durable memory items extracted from report", report_title=report_title)
            return []

        async def _batch_save(repo: MemoryRepository):
            return await repo.batch_create(memories_to_create)

        created_records = await self._execute_with_repo(_batch_save)
        logger.info(
            "Persisted research memories from report",
            count=len(created_records),
            user_id=str(u_uuid),
            job_id=str(j_uuid) if j_uuid else None,
        )

        return [
            MemoryItem(
                id=str(r.id),
                user_id=str(r.user_id),
                job_id=str(r.job_id) if r.job_id else None,
                project_id=r.project_id,
                memory_type=MemoryType(r.memory_type) if r.memory_type in [m.value for m in MemoryType] else MemoryType.FINDING,
                title=r.title,
                content=r.content,
                confidence_score=r.confidence_score,
                confidence=r.confidence_score,
                tags=r.tags or [],
                provenance=r.provenance_json or {},
                source_type="report",
                is_pinned=r.is_pinned,
                access_count=r.access_count,
                created_at=r.created_at.isoformat() if r.created_at else "",
                updated_at=r.updated_at.isoformat() if r.updated_at else "",
            )
            for r in created_records
        ]

    async def recall_memories(
        self,
        query: str,
        user_id: Optional[Union[UUID, str]] = None,
        top_k: int = 5,
        memory_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_confidence: float = 0.70,
    ) -> MemoryRecallResult:
        """Retrieve relevant past research memories matching a query and score threshold."""
        u_uuid = UUID(str(user_id)) if user_id else None

        async def _search(repo: MemoryRepository):
            records = await repo.search_by_text(
                user_id=u_uuid,
                query=query,
                memory_type=memory_type,
                limit=top_k * 2,
            )
            if tags:
                records = [r for r in records if any(t in (r.tags or []) for t in tags)]
            filtered = [r for r in records if (r.confidence_score or 1.0) >= min_confidence][:top_k]
            for r in filtered:
                try:
                    await repo.increment_access(r.id)
                except Exception:
                    pass
            return filtered

        filtered_records = await self._execute_with_repo(_search)

        memory_items = [
            MemoryItem(
                id=str(r.id),
                user_id=str(r.user_id),
                job_id=str(r.job_id) if r.job_id else None,
                project_id=r.project_id,
                memory_type=MemoryType(r.memory_type) if r.memory_type in [m.value for m in MemoryType] else MemoryType.FINDING,
                title=r.title,
                content=r.content,
                confidence_score=r.confidence_score,
                confidence=r.confidence_score,
                tags=r.tags or [],
                provenance=r.provenance_json or {},
                source_type="recalled",
                is_pinned=r.is_pinned,
                access_count=r.access_count + 1,
                created_at=r.created_at.isoformat() if r.created_at else "",
                updated_at=r.updated_at.isoformat() if r.updated_at else "",
            )
            for r in filtered_records
        ]

        prompt_context = self.format_memories_for_prompt(memory_items)

        return MemoryRecallResult(
            memories=memory_items,
            total_found=len(memory_items),
            total_recalled=len(memory_items),
            query=query,
            augmented_prompt_context=prompt_context,
        )

    def format_memories_for_prompt(self, memories: List[MemoryItem]) -> str:
        """Format recalled memories into a clean markdown context block."""
        if not memories:
            return ""

        lines = [
            "### Historical Cross-Session Research Memories:",
            "The following verified facts, findings, concepts, and methodologies were discovered in prior sessions:",
        ]
        for m in memories:
            pin_badge = " 📌 [PINNED]" if m.is_pinned else ""
            type_label = m.memory_type.value.capitalize() if hasattr(m.memory_type, "value") else str(m.memory_type)
            conf_val = m.confidence_score if m.confidence_score is not None else 1.0
            lines.append(
                f"- **[Prior Research {type_label}] {m.title}** (Confidence: {conf_val:.2f}){pin_badge}:\n"
                f"  {m.content}"
            )

        return "\n".join(lines)
