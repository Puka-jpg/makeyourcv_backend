from google.adk.sessions import DatabaseSessionService

from adk.services.custom_session_service import SharedDatabaseSessionService
from db import sessionmanager

_session_service = None


def get_session_service() -> DatabaseSessionService:
    """
    Returns a singleton instance of SharedDatabaseSessionService.
    Ensures ADK uses the same DB pool as the FastAPI app.
    """
    global _session_service
    if _session_service is None:
        _session_service = SharedDatabaseSessionService(session_manager=sessionmanager)
    return _session_service
