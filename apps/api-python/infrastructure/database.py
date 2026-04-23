from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from infrastructure.config import get_settings
from typing import AsyncGenerator, Optional

settings = get_settings()

# For asyncpg, the url needs to be postgresql+asyncpg://
db_url = settings.database_url
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(db_url, echo=settings.debug)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db() -> AsyncGenerator[Optional[AsyncSession], None]:
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except Exception:
        # For demo purposes, we allow the app to continue without a DB
        yield None
