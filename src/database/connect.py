import contextlib
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.conf.config import config


class Base(DeclarativeBase):
    pass


class DatabaseSessionManager:
    """
    Manages database sessions for asynchronous SQLAlchemy operations.

    Args:
        url (str): The database connection URL.

    Attributes:
        _engine (AsyncEngine | None): The SQLAlchemy asynchronous engine.
        _session_maker (async_sessionmaker | None): The asynchronous session maker.

    Methods:
        session(): Asynchronous context manager to acquire and manage database sessions.
    """

    def __init__(self, url: str):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the database connection and sessionmaker, which will be used for all queries.

        :param self: Represent the instance of the class
        :param url: str: Create the engine
        :return: The class instance itself, which is self
        
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker | None = async_sessionmaker(
            autocommit=False, autoflush=False, expire_on_commit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """
        Asynchronous context manager to acquire and manage database sessions.

        Yields:
            AsyncSession: An asynchronous database session.

        Raises:
            Exception: If the DatabaseSessionManager is not properly initialized.
        """
        if self._session_maker is None:
            raise Exception("DatabaseSessionManager is not initialized")
        session = self._session_maker()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()


SQLALCHEMY_DATABASE_URL = (
    "postgresql+asyncpg://"
    + f"{config.postgres_user}:{config.postgres_password}"
    + f"@{config.postgres_host}:{config.postgres_port}"
    + f"/{config.postgres_db}"
)

session_manager = DatabaseSessionManager(SQLALCHEMY_DATABASE_URL)


async def get_database_session():
    """
    Asynchronously gets a database session using the session manager.

    Yields:
        AsyncSession: An asynchronous database session.
    """
    async with session_manager.session() as session:
        yield session
