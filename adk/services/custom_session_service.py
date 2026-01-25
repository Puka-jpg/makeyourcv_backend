from typing import Any

from google.adk.sessions.database_session_service import Base, DatabaseSessionService

from db import SessionManager


class SharedDatabaseSessionService(DatabaseSessionService):
    """
    A custom ADK DatabaseSessionService that reuses the existing application SessionManager.
    This prevents ADK from creating its own DB engine/pool.
    """

    def __init__(self, session_manager: SessionManager):
        """
        Initialize with the application's SessionManager.
        Skips the default engine creation in the parent class.

        Args:
            session_manager: The application's initialized SessionManager instance.
        """
        self._session_manager = session_manager

        self._dialect_name = None
        if self._session_manager.engine:
            self._dialect_name = self._session_manager.engine.dialect.name

        self.database_session_factory = self._session_factory_wrapper  # type: ignore[assignment]

    def _session_factory_wrapper(self) -> Any:
        """
        Wraps the session_manager.session_factory to be compatible with ADK usage.
        ADK calls: async with self.database_session_factory() as sql_session:
        So this function must return the AsyncSession (which is the context manager).
        """
        if not self._session_manager.session_factory:
            raise RuntimeError(
                "SessionManager is not initialized. Call init_db() first."
            )
        return self._session_manager.session_factory()

    async def _ensure_tables_created(self) -> None:
        """
        Ensures ADK tables exist using the shared engine.
        """
        if not self._session_manager.engine:
            raise RuntimeError("SessionManager engine is not initialized.")

        async with self._session_manager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
