from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://myuser:advanced04@localhost/projectdb"

# Async engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

# Base class for models (needed by Alembic)
Base = declarative_base()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine.sync_engine
)

# Async session
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)