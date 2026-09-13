"""Enterprise KMS Envelope Encryption and Cryptographic Hash Chaining Utilities (Phase 23)."""
import base64
from datetime import UTC, datetime
import hashlib
import json
import os
import secrets
from typing import Any, Dict, Optional, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

from shared.exceptions import ValidationError
from shared.logging import get_logger

logger = get_logger(__name__)

# Default master salt derivation if not supplied via environment
_DEFAULT_KMS_SALT = b"agentic-research-platform-kms-salt-2026"


class KMSEnvelopeEncryption:
    """Enterprise-grade AES-256-GCM Envelope Encryption engine.
    
    Protects sensitive credentials (LLM API keys, database connection strings, tokens)
    using two-tier envelope encryption:
    - Master Key derives Key Encryption Key (KEK).
    - Unique Data Encryption Key (DEK) generated per secret.
    - Secret payload is encrypted with DEK (AES-256-GCM authenticated ciphertext).
    - DEK is encrypted with KEK and stored alongside the ciphertext.
    """

    def __init__(self, master_key_secret: Optional[str] = None) -> None:
        raw_key = master_key_secret or os.environ.get("KMS_MASTER_KEY") or "default-platform-kms-development-key-32b"
        self._kek = self._derive_kek(raw_key.encode("utf-8"))

    @staticmethod
    def _derive_kek(raw_key_bytes: bytes) -> bytes:
        """Derive a 256-bit Key Encryption Key using PBKDF2 with SHA-256."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=_DEFAULT_KMS_SALT,
            iterations=100_000,
        )
        return kdf.derive(raw_key_bytes)

    def encrypt_secret(self, plaintext_secret: str) -> Dict[str, str]:
        """Encrypt a secret string using a freshly generated random DEK."""
        if not plaintext_secret:
            raise ValidationError("Secret value cannot be empty")

        # 1. Generate 256-bit ephemeral DEK
        dek = AESGCM.generate_key(bit_length=256)
        
        # 2. Encrypt plaintext secret with DEK (AES-256-GCM)
        dek_aesgcm = AESGCM(dek)
        nonce_dek = os.urandom(12)
        secret_ciphertext = dek_aesgcm.encrypt(nonce_dek, plaintext_secret.encode("utf-8"), None)

        # 3. Encrypt DEK with KEK
        kek_aesgcm = AESGCM(self._kek)
        nonce_kek = os.urandom(12)
        encrypted_dek = kek_aesgcm.encrypt(nonce_kek, dek, None)

        return {
            "encrypted_payload": base64.b64encode(nonce_dek + secret_ciphertext).decode("utf-8"),
            "encrypted_dek": base64.b64encode(nonce_kek + encrypted_dek).decode("utf-8"),
            "key_version": "v1-aes256gcm",
        }

    def decrypt_secret(self, encrypted_payload_b64: str, encrypted_dek_b64: str) -> str:
        """Decrypt a secret by unwrapping the DEK and decrypting the payload."""
        try:
            # 1. Decrypt DEK with KEK
            raw_encrypted_dek = base64.b64decode(encrypted_dek_b64)
            nonce_kek = raw_encrypted_dek[:12]
            ciphertext_dek = raw_encrypted_dek[12:]

            kek_aesgcm = AESGCM(self._kek)
            dek = kek_aesgcm.decrypt(nonce_kek, ciphertext_dek, None)

            # 2. Decrypt payload with DEK
            raw_payload = base64.b64decode(encrypted_payload_b64)
            nonce_dek = raw_payload[:12]
            ciphertext_secret = raw_payload[12:]

            dek_aesgcm = AESGCM(dek)
            plaintext_bytes = dek_aesgcm.decrypt(nonce_dek, ciphertext_secret, None)
            return plaintext_bytes.decode("utf-8")
        except Exception as exc:
            logger.error("KMS decryption failed", error=str(exc))
            raise ValidationError("Failed to decrypt secret payload: authentication tag mismatch or corrupt key")


class AuditHashChainer:
    """Tamper-evident cryptographic hash chaining for security audit logs.
    
    Each audit log record includes the hash of the preceding record, creating a
    cryptographically verifiable blockchain-like merkle sequence:
    CurrentHash = SHA256(PreviousHash + Timestamp + Action + ActorId + TargetResource + Details)
    """

    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    @classmethod
    def compute_record_hash(
        cls,
        previous_hash: Optional[str],
        timestamp: Any,
        event_type: str,
        actor_id: Optional[str],
        resource_id: Optional[str],
        details: Dict[str, Any],
    ) -> str:
        """Calculate deterministic SHA-256 hash chaining record data to previous entry."""
        prev = previous_hash or cls.GENESIS_HASH
        details_serialized = json.dumps(details, sort_keys=True)
        if isinstance(timestamp, datetime):
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=UTC)
            ts_str = str(int(timestamp.timestamp()))
        else:
            ts_str = str(timestamp)
        payload = f"{prev}|{ts_str}|{event_type}|{actor_id or 'system'}|{resource_id or ''}|{details_serialized}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def verify_chain_integrity(cls, log_records: list) -> Tuple[bool, Optional[str]]:
        """Verify the integrity of a sequence of audit log records."""
        if not log_records:
            return True, None

        for i, record in enumerate(log_records):
            if i == 0:
                if record.previous_hash not in (None, cls.GENESIS_HASH):
                    return False, f"Broken chain link at genesis index 0: unexpected previous_hash '{record.previous_hash}'"
            else:
                expected_prev = log_records[i - 1].current_hash
                if record.previous_hash != expected_prev:
                    return False, f"Broken chain link at index {i}: record previous_hash '{record.previous_hash}' != expected '{expected_prev}'"

            computed = cls.compute_record_hash(
                previous_hash=record.previous_hash,
                timestamp=record.created_at,
                event_type=record.event_type,
                actor_id=str(record.actor_id) if record.actor_id else None,
                resource_id=str(record.resource_id) if record.resource_id else None,
                details=record.details or {},
            )
            if computed != record.current_hash:
                return False, f"Tampered record at index {i}: current_hash '{record.current_hash}' != computed '{computed}'"

        return True, None
