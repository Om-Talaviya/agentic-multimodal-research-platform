"""Database connection management."""

from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from shared.config import settings
from shared.logging import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


engine_kwargs = {
    "echo": settings.debug,
}

if not settings.database_url.startswith("sqlite"):
    engine_kwargs.update({
        "pool_size": settings.database_pool_size,
        "max_overflow": settings.database_max_overflow,
        "pool_pre_ping": True,
    })
else:
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_async_engine(settings.database_url, **engine_kwargs)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session() -> AsyncSession:
    """FastAPI dependency yielding database session with automatic commit/rollback."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


get_session = asynccontextmanager(get_db_session)


async def bootstrap_default_users(session: AsyncSession) -> None:
    """Bootstrap default development/system accounts (admin, researcher, viewer) if they do not exist."""
    from database.models.user import User as DBUser
    from database.repositories.user_repo import UserRepository
    from shared.auth import UserRole, hash_password

    repo = UserRepository(session)

    defaults = [
        ("admin", "admin@platform.ai", "AdminPassword123!", UserRole.ADMIN.value),
        ("researcher", "researcher@platform.ai", "ResearcherPassword123!", UserRole.RESEARCHER.value),
        ("viewer", "viewer@platform.ai", "ViewerPassword123!", UserRole.VIEWER.value),
    ]

    for uname, email, pwd, role in defaults:
        existing = await repo.get_by_username(uname)
        if not existing:
            user = DBUser(
                username=uname,
                email=email,
                password_hash=hash_password(pwd),
                role=role,
                is_active=True,
            )
            await repo.create(user)
            logger.info("Bootstrapped default user", username=uname, role=role)


async def init_db() -> None:
    """Initialize database tables and bootstrap default users."""
    logger.info("Initializing database", url=settings.database_url.split("@")[-1])
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")

    async with async_session_maker() as session:
        try:
            await bootstrap_default_users(session)
            await session.commit()
        except Exception as exc:
            await session.rollback()
            logger.warning("Default user bootstrap skipped/failed", error=str(exc))


async def close_db() -> None:
    """Close database connections."""
    logger.info("Closing database connections")
    await engine.dispose()