"""Repository for Enterprise Security Audit Logs, KMS Secrets, and Compliance Policies (Phase 23)."""
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID
from sqlalchemy import desc, func, select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.security import DBEncryptedSecret, DBSecurityAuditLog, DBSecurityPolicy
from database.models.research_job import ResearchJob
from database.models.document import Document
from database.models.memory import DBResearchMemory
from database.models.graph import DBKnowledgeEntity, DBKnowledgeRelation
from database.models.collaboration import DBReportAnnotation
from shared.kms import AuditHashChainer, KMSEnvelopeEncryption
from shared.logging import get_logger

logger = get_logger(__name__)


class SecurityRepository:
    """Handles persistence and cryptographic integrity for security audit logs and secrets."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def log_security_event(
        self,
        event_type: str,
        action: str,
        severity: str = "INFO",
        actor_id: Optional[UUID] = None,
        workspace_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> DBSecurityAuditLog:
        """Create an immutable security audit log entry with SHA-256 hash chaining."""
        event_details = details or {}
        now = datetime.now(UTC)
        now_iso = now.isoformat()

        # 1. Fetch latest audit log record hash for chaining
        latest_stmt = (
            select(DBSecurityAuditLog.current_hash)
            .order_by(desc(DBSecurityAuditLog.created_at), desc(DBSecurityAuditLog.id))
            .limit(1)
        )
        latest_res = await self.session.execute(latest_stmt)
        previous_hash = latest_res.scalar_one_or_none() or AuditHashChainer.GENESIS_HASH

        # 2. Compute cryptographically chained SHA-256 current hash
        current_hash = AuditHashChainer.compute_record_hash(
            previous_hash=previous_hash,
            timestamp=now,
            event_type=event_type,
            actor_id=str(actor_id) if actor_id else None,
            resource_id=str(resource_id) if resource_id else None,
            details=event_details,
        )

        log_entry = DBSecurityAuditLog(
            event_type=event_type,
            severity=severity,
            actor_id=actor_id,
            workspace_id=workspace_id,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            action=action,
            details=event_details,
            ip_address=ip_address,
            user_agent=user_agent,
            previous_hash=previous_hash,
            current_hash=current_hash,
            created_at=now,
        )
        self.session.add(log_entry)
        await self.session.flush()

        logger.info(
            "Security event logged",
            event_type=event_type,
            severity=severity,
            action=action,
            current_hash=current_hash[:12],
        )
        return log_entry

    async def list_audit_logs(
        self,
        workspace_id: Optional[UUID] = None,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[DBSecurityAuditLog]:
        """List audit log records with optional filtering."""
        stmt = select(DBSecurityAuditLog)
        if workspace_id:
            stmt = stmt.where(DBSecurityAuditLog.workspace_id == workspace_id)
        if event_type:
            stmt = stmt.where(DBSecurityAuditLog.event_type == event_type)
        if severity:
            stmt = stmt.where(DBSecurityAuditLog.severity == severity)

        stmt = stmt.order_by(desc(DBSecurityAuditLog.created_at)).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def verify_audit_log_integrity(self, limit: int = 500) -> Dict[str, Any]:
        """Verify the cryptographic hash chain of recent audit records."""
        stmt = select(DBSecurityAuditLog).order_by(DBSecurityAuditLog.created_at.asc()).limit(limit)
        result = await self.session.execute(stmt)
        records = list(result.scalars().all())

        is_valid, error_msg = AuditHashChainer.verify_chain_integrity(records)
        return {
            "verified": is_valid,
            "total_records_checked": len(records),
            "integrity_status": "VALID_TAMPER_EVIDENT" if is_valid else "CORRUPT_OR_TAMPERED",
            "error_detail": error_msg,
            "genesis_hash": AuditHashChainer.GENESIS_HASH,
            "latest_verified_hash": records[-1].current_hash if records else None,
        }

    async def create_encrypted_secret(
        self,
        name: str,
        secret_type: str,
        provider: str,
        plaintext_value: str,
        masked_preview: Optional[str] = None,
        workspace_id: Optional[UUID] = None,
        created_by: Optional[UUID] = None,
        kms: Optional[KMSEnvelopeEncryption] = None,
    ) -> DBEncryptedSecret:
        """Encrypt and store credentials in the KMS vault."""
        kms_engine = kms or KMSEnvelopeEncryption()
        encrypted_dict = kms_engine.encrypt_secret(plaintext_value)

        preview = masked_preview
        if not preview:
            # Generate masked preview: e.g. "sk-...a1b2"
            if len(plaintext_value) > 8:
                preview = f"{plaintext_value[:3]}...{plaintext_value[-4:]}"
            else:
                preview = "********"

        secret = DBEncryptedSecret(
            name=name,
            secret_type=secret_type,
            provider=provider,
            key_version=encrypted_dict["key_version"],
            encrypted_payload=encrypted_dict["encrypted_payload"],
            encrypted_dek=encrypted_dict["encrypted_dek"],
            masked_preview=preview,
            workspace_id=workspace_id,
            created_by=created_by,
        )
        self.session.add(secret)
        await self.session.flush()

        # Log vault storage event
        await self.log_security_event(
            event_type="secret_stored",
            action="vault_encrypt",
            severity="INFO",
            actor_id=created_by,
            workspace_id=workspace_id,
            resource_type="encrypted_secret",
            resource_id=str(secret.id),
            details={"name": name, "provider": provider, "secret_type": secret_type},
        )
        return secret

    async def list_secrets(
        self,
        workspace_id: Optional[UUID] = None,
        provider: Optional[str] = None,
    ) -> List[DBEncryptedSecret]:
        """List secrets in the vault (only returning metadata, not plaintext)."""
        stmt = select(DBEncryptedSecret).where(DBEncryptedSecret.is_revoked == False)
        if workspace_id:
            stmt = stmt.where(DBEncryptedSecret.workspace_id == workspace_id)
        if provider:
            stmt = stmt.where(DBEncryptedSecret.provider == provider)

        stmt = stmt.order_by(desc(DBEncryptedSecret.created_at))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_secret_by_id(self, secret_id: UUID) -> Optional[DBEncryptedSecret]:
        """Fetch secret by ID."""
        stmt = select(DBEncryptedSecret).where(DBEncryptedSecret.id == secret_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def decrypt_secret_value(
        self,
        secret_id: UUID,
        kms: Optional[KMSEnvelopeEncryption] = None,
    ) -> str:
        """Unwrap and decrypt secret plaintext."""
        secret = await self.get_secret_by_id(secret_id)
        if not secret or secret.is_revoked:
            raise ValueError(f"Secret '{secret_id}' not found or has been revoked")

        kms_engine = kms or KMSEnvelopeEncryption()
        return kms_engine.decrypt_secret(
            encrypted_payload_b64=secret.encrypted_payload,
            encrypted_dek_b64=secret.encrypted_dek,
        )

    async def revoke_secret(self, secret_id: UUID, actor_id: Optional[UUID] = None) -> bool:
        """Mark secret as revoked."""
        secret = await self.get_secret_by_id(secret_id)
        if not secret:
            return False

        secret.is_revoked = True
        await self.session.flush()

        await self.log_security_event(
            event_type="secret_revoked",
            action="vault_revoke",
            severity="WARNING",
            actor_id=actor_id,
            workspace_id=secret.workspace_id,
            resource_type="encrypted_secret",
            resource_id=str(secret.id),
            details={"name": secret.name, "provider": secret.provider},
        )
        return True

    async def delete_secret(self, secret_id: UUID, actor_id: Optional[UUID] = None) -> bool:
        """Permanently delete a secret from the vault."""
        secret = await self.get_secret_by_id(secret_id)
        if not secret:
            return False

        await self.session.delete(secret)
        await self.session.flush()

        await self.log_security_event(
            event_type="secret_deleted",
            action="vault_purge",
            severity="WARNING",
            actor_id=actor_id,
            workspace_id=secret.workspace_id,
            resource_type="encrypted_secret",
            resource_id=str(secret_id),
            details={"name": secret.name},
        )
        return True

    async def get_or_create_security_policy(self, workspace_id: UUID) -> DBSecurityPolicy:
        """Get or initialize workspace security policy."""
        stmt = select(DBSecurityPolicy).where(DBSecurityPolicy.workspace_id == workspace_id)
        result = await self.session.execute(stmt)
        policy = result.scalars().first()

        if not policy:
            policy = DBSecurityPolicy(
                workspace_id=workspace_id,
                retention_days=365,
                enforce_mfa=False,
                ip_whitelist={"allowed_cidrs": []},
                allowed_providers={"providers": ["gemini", "ollama", "openai"]},
                gdpr_anonymize_on_delete=True,
                data_classification="CONFIDENTIAL",
            )
            self.session.add(policy)
            await self.session.flush()

        return policy

    async def update_security_policy(
        self,
        workspace_id: UUID,
        retention_days: Optional[int] = None,
        enforce_mfa: Optional[bool] = None,
        ip_whitelist: Optional[Dict[str, Any]] = None,
        allowed_providers: Optional[Dict[str, Any]] = None,
        gdpr_anonymize_on_delete: Optional[bool] = None,
        data_classification: Optional[str] = None,
        actor_id: Optional[UUID] = None,
    ) -> DBSecurityPolicy:
        """Update workspace security and retention parameters."""
        policy = await self.get_or_create_security_policy(workspace_id)

        if retention_days is not None:
            policy.retention_days = retention_days
        if enforce_mfa is not None:
            policy.enforce_mfa = enforce_mfa
        if ip_whitelist is not None:
            policy.ip_whitelist = ip_whitelist
        if allowed_providers is not None:
            policy.allowed_providers = allowed_providers
        if gdpr_anonymize_on_delete is not None:
            policy.gdpr_anonymize_on_delete = gdpr_anonymize_on_delete
        if data_classification is not None:
            policy.data_classification = data_classification

        await self.session.flush()

        await self.log_security_event(
            event_type="security_policy_updated",
            action="policy_configure",
            severity="WARNING",
            actor_id=actor_id,
            workspace_id=workspace_id,
            resource_type="security_policy",
            resource_id=str(policy.id),
            details={
                "retention_days": policy.retention_days,
                "enforce_mfa": policy.enforce_mfa,
                "data_classification": policy.data_classification,
            },
        )
        return policy

    async def execute_gdpr_data_purge(
        self,
        workspace_id: UUID,
        actor_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Cascade-purge or anonymize workspace research data under GDPR Article 17 (Right to be Forgotten)."""
        policy = await self.get_or_create_security_policy(workspace_id)

        # 1. Delete or anonymize research jobs
        jobs_stmt = select(ResearchJob).where(ResearchJob.workspace_id == workspace_id)
        jobs_res = await self.session.execute(jobs_stmt)
        jobs = list(jobs_res.scalars().all())
        jobs_count = len(jobs)
        for j in jobs:
            await self.session.delete(j)

        # 2. Delete documents
        docs_stmt = select(Document).where(Document.workspace_id == workspace_id)
        docs_res = await self.session.execute(docs_stmt)
        docs = list(docs_res.scalars().all())
        docs_count = len(docs)
        for d in docs:
            await self.session.delete(d)

        # 3. Delete research memories
        mems_stmt = select(DBResearchMemory).where(DBResearchMemory.workspace_id == workspace_id)
        mems_res = await self.session.execute(mems_stmt)
        mems = list(mems_res.scalars().all())
        mems_count = len(mems)
        for m in mems:
            await self.session.delete(m)

        # 4. Delete knowledge graph entities
        graph_stmt = select(DBKnowledgeEntity).where(DBKnowledgeEntity.workspace_id == workspace_id)
        graph_res = await self.session.execute(graph_stmt)
        entities = list(graph_res.scalars().all())
        entities_count = len(entities)
        for e in entities:
            await self.session.delete(e)

        await self.session.flush()

        # Log GDPR purge
        await self.log_security_event(
            event_type="gdpr_data_purge",
            action="compliance_purge",
            severity="CRITICAL",
            actor_id=actor_id,
            workspace_id=workspace_id,
            resource_type="workspace",
            resource_id=str(workspace_id),
            details={
                "jobs_purged": jobs_count,
                "documents_purged": docs_count,
                "memories_purged": mems_count,
                "graph_entities_purged": entities_count,
                "compliance_framework": "GDPR_ARTICLE_17",
            },
        )

        return {
            "workspace_id": str(workspace_id),
            "jobs_purged": jobs_count,
            "documents_purged": docs_count,
            "memories_purged": mems_count,
            "graph_entities_purged": entities_count,
            "timestamp": datetime.now(UTC).isoformat(),
            "status": "COMPLETED_GDPR_PURGE",
        }
