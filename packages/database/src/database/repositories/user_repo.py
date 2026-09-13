"""User repository for persistent authentication and profile management."""

from datetime import UTC, datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.user import User


def utc_now() -> datetime:
    return datetime.now(UTC)


class UserRepository:
    """Repository for user entity database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user: User) -> User:
        """Add and persist a new user."""
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieve user by UUID primary key."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Retrieve user by case-insensitive username."""
        result = await self.session.execute(
            select(User).where(func.lower(User.username) == username.lower().strip())
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve user by case-insensitive email."""
        result = await self.session.execute(
            select(User).where(func.lower(User.email) == email.lower().strip())
        )
        return result.scalar_one_or_none()

    async def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        """Retrieve user matching either username or email."""
        cleaned = identifier.lower().strip()
        result = await self.session.execute(
            select(User).where(
                (func.lower(User.username) == cleaned) | (func.lower(User.email) == cleaned)
            )
        )
        return result.scalar_one_or_none()

    async def update_user(
        self,
        user_id: UUID,
        *,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        password_hash: Optional[str] = None,
    ) -> Optional[User]:
        """Update user properties."""
        values: dict = {"updated_at": utc_now()}
        if role is not None:
            values["role"] = role
        if is_active is not None:
            values["is_active"] = is_active
        if password_hash is not None:
            values["password_hash"] = password_hash

        await self.session.execute(
            update(User).where(User.id == user_id).values(**values)
        )
        await self.session.flush()
        return await self.get_by_id(user_id)

    async def list_users(self, limit: int = 50, offset: int = 0) -> List[User]:
        """List active users with pagination."""
        result = await self.session.execute(
            select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())
