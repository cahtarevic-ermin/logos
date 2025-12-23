from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import async_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
