"""
MediKiosk Database Infrastructure.

Provides the async SQLAlchemy engine, session factory, and FastAPI dependency
for per-request database sessions.

Architecture:
    - Engine is created once at application startup via init_db().
    - Each FastAPI request gets its own AsyncSession via get_db_session().
    - The session is committed on success, rolled back on failure.
    - All ORM models inherit from Base (DeclarativeBase).

Usage:
    # In main.py lifespan:
    await init_db(settings.database_url)

    # In FastAPI endpoints:
    async def create_session(db: AsyncSession = Depends(get_db_session)):
        ...
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all MediKiosk ORM models."""

    pass


# Module-level engine and session factory — initialised at startup.
_engine: AsyncEngine | None = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


async def init_db(database_url: str, echo: bool = False) -> None:
    """
    Initialise the database engine and session factory.

    Called once during application startup (lifespan handler).

    Args:
        database_url: SQLAlchemy database URL
                      (e.g., 'postgresql+asyncpg://...' or 'sqlite+aiosqlite://...').
        echo: If True, log all SQL statements (for development only).
    """
    global _engine, _async_session_factory

    _engine = create_async_engine(
        database_url,
        echo=echo,
        future=True,
    )
    _async_session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def close_db() -> None:
    """
    Dispose the database engine and release connections.

    Called during application shutdown (lifespan handler).
    """
    global _engine, _async_session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_factory = None


def get_engine() -> AsyncEngine:
    """Return the current async engine. Raises if not initialised."""
    if _engine is None:
        raise RuntimeError(
            "Database engine not initialised. Call init_db() first."
        )
    return _engine


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an async database session.

    The session is committed on success and rolled back on exception.
    This function is used as a FastAPI Depends() provider.

    Yields:
        AsyncSession bound to the current request.

    Raises:
        RuntimeError: If the database has not been initialised.
    """
    if _async_session_factory is None:
        raise RuntimeError(
            "Database session factory not initialised. Call init_db() first."
        )

    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_all_tables() -> None:
    """
    Create all tables defined by Base.metadata.

    Used for development and testing only. In production, use Alembic migrations.
    """
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
