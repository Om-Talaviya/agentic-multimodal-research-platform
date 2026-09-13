import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.models.security import DBSecurityAuditLog, DBEncryptedSecret, DBSecurityPolicy
from database.repositories.security_repo import SecurityRepository
from shared.kms import KMSEnvelopeEncryption

@pytest.fixture
async def async_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_factory() as session:
        yield session
    await engine.dispose()

@pytest.mark.asyncio
async def test_security_audit_log_hash_chain(async_session: AsyncSession):
    repo = SecurityRepository(async_session)
    actor_id = uuid.uuid4()
    ws_id = uuid.uuid4()

    # Log 3 events
    log1 = await repo.log_security_event(
        event_type="user.login",
        action="login_success",
        severity="INFO",
        actor_id=actor_id,
        workspace_id=ws_id,
        details={"ip": "127.0.0.1"}
    )
    assert log1.previous_hash == "0000000000000000000000000000000000000000000000000000000000000000"
    assert log1.current_hash is not None

    log2 = await repo.log_security_event(
        event_type="secret.access",
        action="decrypt_key",
        severity="WARNING",
        actor_id=actor_id,
        workspace_id=ws_id,
        details={"key": "gemini"}
    )
    assert log2.previous_hash == log1.current_hash

    log3 = await repo.log_security_event(
        event_type="export.report",
        action="export_pdf",
        severity="INFO",
        actor_id=actor_id,
        workspace_id=ws_id,
        details={"format": "pdf"}
    )
    assert log3.previous_hash == log2.current_hash

    # Verify integrity
    integrity_res = await repo.verify_audit_log_integrity()
    assert integrity_res["verified"] is True
    assert integrity_res["integrity_status"] == "VALID_TAMPER_EVIDENT"
    assert integrity_res["total_records_checked"] == 3

@pytest.mark.asyncio
async def test_kms_secret_vault_lifecycle(async_session: AsyncSession):
    repo = SecurityRepository(async_session)
    kms = KMSEnvelopeEncryption(master_key_secret="test-encryption-key-for-db-tests")
    actor_id = uuid.uuid4()
    ws_id = uuid.uuid4()

    # Create secret
    secret = await repo.create_encrypted_secret(
        name="Production Gemini API Key",
        secret_type="api_key",
        provider="gemini",
        plaintext_value="AIzaSyA_UltraSecretKey1234567890",
        workspace_id=ws_id,
        created_by=actor_id,
        kms=kms,
    )
    assert secret.id is not None
    assert secret.masked_preview == "AIz...7890"
    assert secret.encrypted_payload != "AIzaSyA_UltraSecretKey1234567890"

    # Decrypt secret
    decrypted = await repo.decrypt_secret_value(secret.id, kms=kms)
    assert decrypted == "AIzaSyA_UltraSecretKey1234567890"

    # Revoke secret
    revoked = await repo.revoke_secret(secret.id, actor_id=actor_id)
    assert revoked is True

    # Decrypting revoked secret must fail
    with pytest.raises(ValueError, match="revoked"):
        await repo.decrypt_secret_value(secret.id, kms=kms)

@pytest.mark.asyncio
async def test_security_policy_and_gdpr_purge(async_session: AsyncSession):
    repo = SecurityRepository(async_session)
    ws_id = uuid.uuid4()
    actor_id = uuid.uuid4()

    # Get or create policy
    policy = await repo.get_or_create_security_policy(ws_id)
    assert policy.retention_days == 365
    assert policy.data_classification == "CONFIDENTIAL"

    # Update policy
    updated = await repo.update_security_policy(
        workspace_id=ws_id,
        retention_days=90,
        enforce_mfa=True,
        data_classification="RESTRICTED",
        actor_id=actor_id,
    )
    assert updated.retention_days == 90
    assert updated.enforce_mfa is True
    assert updated.data_classification == "RESTRICTED"

    # Execute GDPR purge
    purge_res = await repo.execute_gdpr_data_purge(ws_id, actor_id=actor_id)
    assert purge_res["status"] == "COMPLETED_GDPR_PURGE"
    assert purge_res["workspace_id"] == str(ws_id)
