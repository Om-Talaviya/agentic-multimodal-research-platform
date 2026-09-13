"""
Developer API Key Repository (Phase 25).
Handles secure key generation, SHA-256 verification, permission scopes, and in-memory token-bucket rate limiting.
"""

from datetime import datetime, timezone, timedelta
import hashlib
import secrets
import time
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.api_key import DBApiKey


# In-memory sliding window rate limiter state: {key_id: [(timestamp)]}
_RATE_LIMIT_WINDOWS: Dict[str, List[float]] = {}


class ApiKeyRepository:
    """Repository for managing Developer API keys and authentication."""

    TIER_RPM_MAP = {
        "free": 60,
        "pro": 300,
        "enterprise": 1200,
    }

    @staticmethod
    def hash_key(raw_key: str) -> str:
        """Computes deterministic SHA-256 hash of a raw API key."""
        return hashlib.sha256(raw_key.strip().encode("utf-8")).hexdigest()

    @staticmethod
    def generate_raw_key() -> str:
        """Generates a cryptographically strong API key string with standard prefix."""
        random_hex = secrets.token_hex(24)
        return f"amrp_live_{random_hex}"

    async def create_api_key(
        self,
        session: AsyncSession,
        user_id: UUID,
        name: str,
        scopes: Optional[List[str]] = None,
        rate_limit_tier: str = "free",
        workspace_id: Optional[UUID] = None,
        expires_in_days: Optional[int] = None,
    ) -> Tuple[DBApiKey, str]:
        """
        Creates a new Developer API Key.
        Returns the persistent DBApiKey record and the raw secret string (shown only once).
        """
        raw_key = self.generate_raw_key()
        key_hash = self.hash_key(raw_key)
        key_prefix = raw_key[:14]  # e.g. "amrp_live_1a2b"

        tier = rate_limit_tier.lower() if rate_limit_tier else "free"
        rpm = self.TIER_RPM_MAP.get(tier, 60)
        
        default_scopes = [
            "research:read",
            "research:write",
            "documents:read",
            "documents:write",
            "memory:read",
            "graph:read",
        ]
        assigned_scopes = scopes if scopes is not None else default_scopes

        expires_at = None
        if expires_in_days and expires_in_days > 0:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        api_key_record = DBApiKey(
            user_id=user_id,
            workspace_id=workspace_id,
            name=name,
            key_prefix=key_prefix,
            key_hash=key_hash,
            scopes=assigned_scopes,
            rate_limit_tier=tier,
            rate_limit_rpm=rpm,
            is_active=True,
            expires_at=expires_at,
        )

        session.add(api_key_record)
        await session.commit()
        await session.refresh(api_key_record)

        return api_key_record, raw_key

    async def authenticate_api_key(
        self,
        session: AsyncSession,
        raw_key: str,
    ) -> Optional[DBApiKey]:
        """
        Authenticates a raw developer API key by SHA-256 hash comparison.
        Verifies active state and non-expiration, updating last_used_at.
        """
        if not raw_key or not raw_key.startswith("amrp_live_"):
            return None

        target_hash = self.hash_key(raw_key)
        prefix = raw_key[:14]

        stmt = select(DBApiKey).where(
            and_(
                DBApiKey.key_prefix == prefix,
                DBApiKey.key_hash == target_hash,
                DBApiKey.is_active.is_(True),
            )
        )
        result = await session.execute(stmt)
        key_record = result.scalars().first()

        if not key_record:
            return None

        # Check expiration with naive/aware datetime handling
        if key_record.expires_at:
            exp = key_record.expires_at
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < datetime.now(timezone.utc):
                return None

        # Update last_used_at timestamp
        key_record.last_used_at = datetime.now(timezone.utc)
        await session.commit()
        await session.refresh(key_record)

        return key_record

    async def list_api_keys(
        self,
        session: AsyncSession,
        user_id: UUID,
        workspace_id: Optional[UUID] = None,
    ) -> List[DBApiKey]:
        """Lists all API keys created by a user or scoped to a workspace."""
        filters = [DBApiKey.user_id == user_id]
        if workspace_id:
            filters.append(DBApiKey.workspace_id == workspace_id)

        stmt = select(DBApiKey).where(and_(*filters)).order_by(DBApiKey.created_at.desc())
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_api_key(
        self,
        session: AsyncSession,
        key_id: UUID,
        user_id: Optional[UUID] = None,
    ) -> Optional[DBApiKey]:
        """Fetches a specific API key by ID."""
        filters = [DBApiKey.id == key_id]
        if user_id:
            filters.append(DBApiKey.user_id == user_id)

        stmt = select(DBApiKey).where(and_(*filters))
        result = await session.execute(stmt)
        return result.scalars().first()

    async def revoke_api_key(
        self,
        session: AsyncSession,
        key_id: UUID,
        user_id: Optional[UUID] = None,
    ) -> bool:
        """Revokes (deactivates) an API key."""
        key_record = await self.get_api_key(session, key_id, user_id)
        if not key_record:
            return False

        key_record.is_active = False
        await session.commit()
        return True

    async def delete_api_key(
        self,
        session: AsyncSession,
        key_id: UUID,
        user_id: Optional[UUID] = None,
    ) -> bool:
        """Permanently deletes an API key record."""
        key_record = await self.get_api_key(session, key_id, user_id)
        if not key_record:
            return False

        await session.delete(key_record)
        await session.commit()
        return True

    @staticmethod
    def check_rate_limit(key_id: str, rpm: int) -> Tuple[bool, int, int]:
        """
        Sliding 60-second window rate limit checker.
        Returns: (allowed: bool, remaining_requests: int, retry_after_seconds: int)
        """
        now = time.time()
        window_start = now - 60.0

        timestamps = _RATE_LIMIT_WINDOWS.get(key_id, [])
        # Evict timestamps older than 60s
        recent = [ts for ts in timestamps if ts > window_start]
        
        if len(recent) >= rpm:
            oldest_in_window = min(recent) if recent else now
            retry_after = max(1, int(60.0 - (now - oldest_in_window)))
            _RATE_LIMIT_WINDOWS[key_id] = recent
            return False, 0, retry_after

        recent.append(now)
        _RATE_LIMIT_WINDOWS[key_id] = recent
        remaining = max(0, rpm - len(recent))
        return True, remaining, 0
