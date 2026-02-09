"""Database setup and session management for SQLite with async support."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

# SQLite database file in project root
DATABASE_URL = "sqlite+aiosqlite:///./maple_return.db"

# Create async engine with echo enabled for development
engine = create_async_engine(DATABASE_URL, echo=True)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Create declarative base for ORM models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency function that yields database sessions.

    Used as a FastAPI dependency to provide database access to route handlers.
    Ensures proper session lifecycle management with automatic cleanup.
    """
    async with AsyncSessionLocal() as session:
        yield session
