from typing import AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings
from typing import AsyncGenerator
import logging

logger = logging.getLogger(__name__)

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.SQLALCHEMY_ECHO,  # TODO False in prod
    pool_pre_ping=True,
    pool_recycle=3600
)

AsyncSessionFactory = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to get an async database session.
    Manages the session lifecycle and transaction.
    """
    async with AsyncSessionFactory() as session:
        logger.debug(f"DB Session {id(session)} created.")
        try:
            yield session
            await session.commit()
            logger.debug(f"DB Session {id(session)} committed.")
        except Exception as e:
            logger.error(f"DB Session {id(session)} rolling back due to: {e}")
            await session.rollback()
            raise
        finally:
            logger.debug(f"DB Session {id(session)} closed.")
