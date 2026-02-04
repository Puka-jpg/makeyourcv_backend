from google.adk.sessions import DatabaseSessionService

from settings import settings

db_url = settings.DB_URL


def get_session_service() -> DatabaseSessionService:
    """
    Returns a singleton instance of DatabaseSessionService.
    Ensures ADK uses the same DB pool as the FastAPI app.
    """
    session_service = DatabaseSessionService(db_url=db_url)
    return session_service
