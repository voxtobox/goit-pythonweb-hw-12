import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import settings


class DatabaseSessionManager:
    """
    Manages the creation and lifecycle of asynchronous database sessions.
    Provides an async context manager for safe session handling.
    """

    def __init__(self, url: str):
        # Initialize the asynchronous engine and session maker using the provided database URL.
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Asynchronous context manager for database session handling.
        Ensures that sessions are properly closed and rolled back in case of errors.
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            # Roll back the session if a database error occurs.
            await session.rollback()
            raise  # Re-raise the original error for upstream handling
        finally:
            # Ensure the session is closed to release resources.
            await session.close()


# Global instance of DatabaseSessionManager configured with the application's database URL.
sessionmanager = DatabaseSessionManager(settings.DB_URL)


async def get_db():
    """
    Dependency function for retrieving a database session in async contexts.
    Used in FastAPI dependency injection to provide a session per request.
    """
    async with sessionmanager.session() as session:
        yield session
