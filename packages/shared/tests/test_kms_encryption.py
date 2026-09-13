import pytest
from datetime import datetime, timezone
from shared.kms import KMSEnvelopeEncryption, AuditHashChainer
from shared.exceptions import ValidationError

def test_kms_envelope_encryption_roundtrip():
    kms = KMSEnvelopeEncryption(master_key_secret="test-master-key-32b-secure-phrase")
    secret = "sk-ant-api03-ultra-secret-token-for-gemini-and-anthropic"

    encrypted = kms.encrypt_secret(secret)
    assert "encrypted_payload" in encrypted
    assert "encrypted_dek" in encrypted
    assert encrypted["key_version"] == "v1-aes256gcm"

    # Ciphertext must not match plaintext
    assert secret not in encrypted["encrypted_payload"]

    # Decrypt and verify match
    decrypted = kms.decrypt_secret(encrypted["encrypted_payload"], encrypted["encrypted_dek"])
    assert decrypted == secret

def test_kms_envelope_encryption_empty_fails():
    kms = KMSEnvelopeEncryption()
    with pytest.raises(ValidationError):
        kms.encrypt_secret("")

def test_kms_envelope_tampered_payload_fails():
    kms = KMSEnvelopeEncryption()
    secret = "my-db-password"
    encrypted = kms.encrypt_secret(secret)
    
    # Tamper with encrypted payload
    tampered_payload = encrypted["encrypted_payload"][:-4] + "AAAA"
    with pytest.raises(ValidationError):
        kms.decrypt_secret(tampered_payload, encrypted["encrypted_dek"])

def test_audit_hash_chain_verification():
    class MockRecord:
        def __init__(self, prev_hash, ts, event, actor, res, details):
            self.previous_hash = prev_hash
            self.created_at = ts
            self.event_type = event
            self.actor_id = actor
            self.resource_id = res
            self.details = details
            self.current_hash = AuditHashChainer.compute_record_hash(
                prev_hash,
                ts,
                event,
                actor,
                res,
                details
            )

    t0 = datetime(2026, 9, 13, 12, 0, 0, tzinfo=timezone.utc)
    t1 = datetime(2026, 9, 13, 12, 1, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 9, 13, 12, 2, 0, tzinfo=timezone.utc)

    r0 = MockRecord(None, t0, "auth.login", "user-1", None, {"ip": "127.0.0.1"})
    r1 = MockRecord(r0.current_hash, t1, "secret.access", "user-1", "sec-1", {"provider": "gemini"})
    r2 = MockRecord(r1.current_hash, t2, "gdpr.purge", "user-1", "user-1", {"scope": "all"})

    valid, err = AuditHashChainer.verify_chain_integrity([r0, r1, r2])
    assert valid is True
    assert err is None

    # Tampering test: modify details of r1
    r1.details = {"ip": "192.168.1.1"}
    valid, err = AuditHashChainer.verify_chain_integrity([r0, r1, r2])
    assert valid is False
    assert "Tampered record at index 1" in err
