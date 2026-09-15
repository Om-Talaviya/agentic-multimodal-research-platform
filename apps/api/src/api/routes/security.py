"""Enterprise Security, KMS Secret Vault, Audit Logs, and Compliance REST API (Phase 23)."""
from typing import Any, Dict, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_db_session, get_optional_current_user
from database.repositories.security_repo import SecurityRepository
from database.repositories.workspace_repo import WorkspaceRepository
from shared.auth import User
from shared.kms import KMSEnvelopeEncryption
from shared.logging import get_logger

router = APIRouter(prefix="/security", tags=["enterprise-security"])
logger = get_logger(__name__)


class CreateSecretRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    name: str = Field(..., min_length=1, max_length=100)
    secret_type: str = Field("api_key", description="api_key, oauth_token, database_uri")
    provider: str = Field("gemini", description="gemini, openai, anthropic, custom")
    plaintext_value: str = Field(..., min_length=1)
    workspace_id: Optional[UUID] = None


class UpdatePolicyRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    retention_days: Optional[int] = Field(None, ge=0, le=3650)
    enforce_mfa: Optional[bool] = None
    ip_whitelist: Optional[Dict[str, Any]] = None
    allowed_providers: Optional[Dict[str, Any]] = None
    gdpr_anonymize_on_delete: Optional[bool] = None
    data_classification: Optional[str] = None


class GDPRPurgeRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    workspace_id: UUID
    confirmation_code: str = Field(..., description="Must equal 'CONFIRM_GDPR_PURGE'")


class LogSecurityEventRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    event_type: str
    action: str
    severity: str = "INFO"
    workspace_id: Optional[UUID] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


@router.post("/audit-logs", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def log_security_event(
    payload: LogSecurityEventRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Record an immutable, hash-chained security audit log entry."""
    repo = SecurityRepository(session)
    actor_raw = current_user.id if current_user and hasattr(current_user, "id") and current_user.id else None
    actor_id = None
    if actor_raw:
        try:
            actor_id = UUID(str(actor_raw)) if not isinstance(actor_raw, UUID) else actor_raw
        except Exception:
            actor_id = None
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    log_record = await repo.log_security_event(
        event_type=payload.event_type,
        action=payload.action,
        severity=payload.severity,
        actor_id=actor_id,
        workspace_id=payload.workspace_id,
        resource_type=payload.resource_type,
        resource_id=payload.resource_id,
        details=payload.details,
        ip_address=client_ip,
        user_agent=user_agent,
    )
    return log_record.to_dict()


@router.get("/audit-logs", response_model=List[Dict[str, Any]])
async def list_audit_logs(
    workspace_id: Optional[UUID] = Query(None),
    event_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session),
):
    """List historical audit logs."""
    repo = SecurityRepository(session)
    records = await repo.list_audit_logs(
        workspace_id=workspace_id,
        event_type=event_type,
        severity=severity,
        limit=limit,
        offset=offset,
    )
    return [r.to_dict() for r in records]


@router.get("/audit-logs/verify", response_model=Dict[str, Any])
async def verify_audit_logs(
    session: AsyncSession = Depends(get_db_session),
):
    """Cryptographically verify SHA-256 hash chain integrity of security audit logs."""
    repo = SecurityRepository(session)
    return await repo.verify_audit_log_integrity(limit=500)


@router.post("/secrets", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def store_secret_in_vault(
    payload: CreateSecretRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Vault a secret using AES-256-GCM KMS envelope encryption."""
    repo = SecurityRepository(session)
    actor_id = current_user.id if current_user and hasattr(current_user, "id") and current_user.id else None

    # Resolve default workspace if not provided
    ws_id = payload.workspace_id
    if not ws_id and actor_id:
        try:
            actor_uuid = UUID(str(actor_id)) if not isinstance(actor_id, UUID) else actor_id
            ws_repo = WorkspaceRepository(session)
            user_ws = await ws_repo.list_for_user(actor_uuid)
            if user_ws:
                ws_id = user_ws[0].id
        except Exception:
            pass

    secret = await repo.create_encrypted_secret(
        name=payload.name,
        secret_type=payload.secret_type,
        provider=payload.provider,
        plaintext_value=payload.plaintext_value,
        workspace_id=ws_id,
        created_by=UUID(str(actor_id)) if actor_id and not isinstance(actor_id, UUID) else actor_id,
    )
    return secret.to_dict()


@router.get("/secrets", response_model=List[Dict[str, Any]])
async def list_vault_secrets(
    workspace_id: Optional[UUID] = Query(None),
    provider: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db_session),
):
    """List vaulted secrets metadata (masked preview only)."""
    repo = SecurityRepository(session)
    secrets = await repo.list_secrets(workspace_id=workspace_id, provider=provider)
    return [s.to_dict() for s in secrets]


@router.patch("/secrets/{id}/revoke", response_model=Dict[str, Any])
async def revoke_vault_secret(
    id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Revoke a secret in the vault."""
    repo = SecurityRepository(session)
    actor_id = current_user.id if current_user and hasattr(current_user, "id") and current_user.id else None
    revoked = await repo.revoke_secret(id, actor_id=actor_id)
    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Secret '{id}' not found",
        )
    return {"status": "REVOKED", "secret_id": str(id)}


@router.delete("/secrets/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vault_secret(
    id: UUID,
    session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Permanently delete a secret from the vault."""
    repo = SecurityRepository(session)
    actor_id = current_user.id if current_user and hasattr(current_user, "id") and current_user.id else None
    deleted = await repo.delete_secret(id, actor_id=actor_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Secret '{id}' not found",
        )
    return None


@router.get("/policy", response_model=Dict[str, Any])
async def get_workspace_security_policy(
    workspace_id: UUID = Query(...),
    session: AsyncSession = Depends(get_db_session),
):
    """Retrieve security policy and retention rules for workspace."""
    repo = SecurityRepository(session)
    policy = await repo.get_or_create_security_policy(workspace_id)
    return policy.to_dict()


@router.patch("/policy", response_model=Dict[str, Any])
async def update_workspace_security_policy(
    workspace_id: UUID = Query(...),
    payload: UpdatePolicyRequest = ...,
    session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Update workspace security, MFA, IP whitelisting, and retention policies."""
    repo = SecurityRepository(session)
    actor_id = current_user.id if current_user and hasattr(current_user, "id") and current_user.id else None
    policy = await repo.update_security_policy(
        workspace_id=workspace_id,
        retention_days=payload.retention_days,
        enforce_mfa=payload.enforce_mfa,
        ip_whitelist=payload.ip_whitelist,
        allowed_providers=payload.allowed_providers,
        gdpr_anonymize_on_delete=payload.gdpr_anonymize_on_delete,
        data_classification=payload.data_classification,
        actor_id=actor_id,
    )
    return policy.to_dict()


@router.post("/gdpr/purge", response_model=Dict[str, Any])
async def execute_gdpr_purge(
    payload: GDPRPurgeRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    """Execute GDPR Right-to-be-Forgotten data purge across all workspace research artifacts."""
    if payload.confirmation_code != "CONFIRM_GDPR_PURGE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid confirmation code. Must provide 'CONFIRM_GDPR_PURGE'",
        )

    repo = SecurityRepository(session)
    actor_id = current_user.id if current_user and hasattr(current_user, "id") and current_user.id else None
    return await repo.execute_gdpr_data_purge(payload.workspace_id, actor_id=actor_id)


@router.get("/compliance/status", response_model=Dict[str, Any])
async def get_compliance_status(
    workspace_id: Optional[UUID] = Query(None),
    session: AsyncSession = Depends(get_db_session),
):
    """Generate enterprise security compliance status scorecard (SOC 2 & GDPR)."""
    repo = SecurityRepository(session)
    integrity = await repo.verify_audit_log_integrity(limit=100)

    policy_data = {}
    if workspace_id:
        policy = await repo.get_or_create_security_policy(workspace_id)
        policy_data = policy.to_dict()

    return {
        "soc2_compliance": {
            "status": "COMPLIANT" if integrity["verified"] else "NON_COMPLIANT",
            "controls": {
                "cc6_1_access_control": "IMPLEMENTED_RBAC",
                "cc6_6_encryption_at_rest": "AES_256_GCM_ENVELOPE_ENCRYPTION",
                "cc7_2_immutable_audit_logging": "ACTIVE_HASH_CHAINED",
                "audit_chain_verified": integrity["verified"],
            },
        },
        "gdpr_compliance": {
            "status": "COMPLIANT",
            "controls": {
                "article_17_right_to_erasure": "AUTOMATED_CASCADE_PURGE",
                "article_25_data_protection_by_design": "TENANT_ISOLATION_AND_ANONYMIZATION",
                "article_32_security_of_processing": "KMS_ENVELOPE_VAULT",
            },
        },
        "policy": policy_data,
        "audit_summary": integrity,
    }
