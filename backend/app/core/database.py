"""
Database connection and session management
Async PostgreSQL with connection pooling
"""

from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.core.config import settings


# Create async engine with connection pooling
async_engine = create_async_engine(
    settings.db.DATABASE_URL,
    pool_size=settings.db.POOL_SIZE,
    max_overflow=settings.db.MAX_OVERFLOW,
    pool_timeout=settings.db.POOL_TIMEOUT,
    pool_recycle=settings.db.POOL_RECYCLE,
    pool_pre_ping=True,  # Health check connections
    echo=settings.app.DEBUG,  # Log SQL in debug mode
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for all models
Base = declarative_base()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database session
    
    Usage:
        @app.get("/")
        async def endpoint(db: AsyncSession = Depends(get_async_session)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions in background tasks
    
    Usage:
        async with get_session_context() as session:
            ...
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def init_db():
    """Initialize database tables"""
    async with async_engine.begin() as conn:
        # Import all models here to ensure they're registered
        from app.models import employee, analytics, user
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections"""
    await async_engine.dispose()


# Sync engine for Alembic migrations and sync operations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

sync_engine = create_engine(
    settings.db.SYNC_DATABASE_URL,
    pool_size=settings.db.POOL_SIZE,
    max_overflow=settings.db.MAX_OVERFLOW,
    pool_timeout=settings.db.POOL_TIMEOUT,
    pool_recycle=settings.db.POOL_RECYCLE,
    pool_pre_ping=True,
)

# Sync session factory
SessionLocal = sessionmaker(
    bind=sync_engine,
    class_=Session,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


def get_db():
    """
    Dependency for getting sync database session
    
    Usage:
        @app.get("/")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
